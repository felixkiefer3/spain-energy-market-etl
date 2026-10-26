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
    last_date = get_last_timestamp('energy_master')
    
    if last_date:
        start = (pd.to_datetime(last_date) + pd.Timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
        logger.info(f"Incremental load starting from {start}")
    else:
        start = '2026-10-01T00:00:00'
        logger.info("Initial full load")

    end = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    
    logger.info("Extracting all data asynchronously...")
    df_price_raw, df_gen_raw = await extract_all_data('600', TECH_IDS, start, end)
    
    if df_price_raw.empty or df_gen_raw.empty:
        logger.warning("No new data available.")
        return

    logger.info("Transforming data...")
    df_price_clean = transform_price_data(df_price_raw)
    df_gen_clean = transform_generation_data(df_gen_raw)
    df_master = create_master_table(df_price_clean, df_gen_clean)
    
    logger.info("Loading master data into database...")
    load_data(df_master, 'energy_master')
    logger.info("Pipeline execution completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())