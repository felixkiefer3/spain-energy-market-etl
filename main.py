import os
import asyncio
import pandas as pd
from datetime import datetime, timezone
from src.extract import extract_all_data
from src.transform import transform_price_data, transform_generation_data, create_master_table
from src.load import load_data, get_last_timestamp
from src.config import TECH_IDS
from src.logger import setup_logger

logger = setup_logger()

async def main():
    """
    Orchestrates the ETL pipeline execution.
    
    Implements incremental loading by checking the last database timestamp. 
    If no history exists, it defaults to an initial start date defined in 
    environment variables. Extracts data asynchronously, transforms it 
    applying business rules, and loads it into the database.
    """
    try:
        last_date = get_last_timestamp('energy_master')

        if last_date:
            start_api = (pd.to_datetime(last_date) - pd.Timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.info(f"Incremental load. Fetching API context from {start_api}")
        else:
            start_api = os.getenv('INITIAL_START_DATE', '2026-01-01T00:00:00Z')
            logger.info(f"Initial full load starting from {start_api}")

        end = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
        logger.info("Extracting all data asynchronously...")
        df_price_raw, df_gen_raw = await extract_all_data('600', TECH_IDS, start_api, end)

        if df_price_raw.empty or df_gen_raw.empty:
            logger.warning(f"Missing data. Prices empty: {df_price_raw.empty} | Gen empty: {df_gen_raw.empty}")
            return
    
        logger.info("Transforming data...")
        df_price_clean = transform_price_data(df_price_raw)
        df_gen_clean = transform_generation_data(df_gen_raw)
        df_master = create_master_table(df_price_clean, df_gen_clean)
        
        if last_date:
            df_master = df_master[df_master['timestamp'] > pd.to_datetime(last_date)]
            
        if df_master.empty:
            logger.info("No new rows to insert after applying overlap filter.")
            return
            
        logger.info("Loading master data into database...")
        load_data(df_master, 'energy_master')
        logger.info(f"Pipeline execution completed successfully! {len(df_master)} rows inserted.")
        
    except Exception as e:
        logger.exception("Fatal error occurred during pipeline execution.")
        raise

if __name__ == "__main__":
    asyncio.run(main())