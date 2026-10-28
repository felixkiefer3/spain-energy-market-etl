import asyncio
import argparse
import pandas as pd
from datetime import datetime
from src.extract import extract_all_data
from src.transform import transform_price_data, transform_generation_data, create_master_table
from src.load import load_data, get_last_timestamp
from src.config import TECH_IDS
from src.logger import setup_logger

logger = setup_logger()

async def load_historical_data(start_date: str, end_date: str):
    """
    Executes a historical data backfill with resume capability and time-chunking.
    
    Checks the database for the last inserted record. If found, overrides the 
    requested start date to resume exactly where it left off, preventing duplicate 
    downloads. Splits the remaining time range into monthly intervals to prevent 
    API timeouts and manage memory footprint.
    
    Args:
        start_date (str): The requested start date in 'YYYY-MM-DD' format.
        end_date (str): The requested end date in 'YYYY-MM-DD' format.
    """
    # 1. Resume Capability: Check DB and override start_date if history exists
    last_date = get_last_timestamp('energy_master')
    if last_date:
        next_start = pd.to_datetime(last_date) + pd.Timedelta(hours=1)
        if next_start > pd.to_datetime(start_date):
            logger.info(f"Database checkpoint found ({last_date}). Fast-forwarding start date.")
            start_date = next_start.strftime('%Y-%m-%dT%H:%M:%S')

    start_ts = pd.to_datetime(start_date, utc=True)
    end_ts = pd.to_datetime(end_date, utc=True)

    if start_ts >= end_ts:
        logger.info("Requested end date has already been reached. Nothing to load.")
        return

    # 2. Robust Chunking: Safely combine mid-month starts with standard month boundaries
    month_starts = pd.date_range(start=start_ts.floor('D'), end=end_ts.floor('D'), freq='MS', tz='UTC')
    date_ranges = pd.DatetimeIndex([start_ts]).union(month_starts).union([end_ts]).unique().sort_values()
    date_ranges = date_ranges[(date_ranges >= start_ts) & (date_ranges <= end_ts)]

    logger.info(f"Starting historical backfill from {start_ts} to {end_ts}")

    for i in range(len(date_ranges) - 1):
        chunk_start = date_ranges[i].strftime('%Y-%m-%dT%H:%M:%SZ')
        chunk_end = date_ranges[i+1].strftime('%Y-%m-%dT%H:%M:%SZ')
        
        logger.info(f"Processing chunk: {chunk_start} to {chunk_end}")
        
        try:
            df_price_raw, df_gen_raw = await extract_all_data('600', TECH_IDS, chunk_start, chunk_end)
            
            if not df_price_raw.empty and not df_gen_raw.empty:
                df_price_clean = transform_price_data(df_price_raw)
                df_gen_clean = transform_generation_data(df_gen_raw)
                df_master = create_master_table(df_price_clean, df_gen_clean)
                
                load_data(df_master, 'energy_master')
                logger.info(f"Chunk loaded successfully: {len(df_master)} rows inserted.")
            else:
                logger.warning(f"Missing data. Prices empty: {df_price_raw.empty} | Gen empty: {df_gen_raw.empty}")
            
            await asyncio.sleep(3)
            
        except Exception:
            logger.exception(f"Failed to process chunk {chunk_start} - {chunk_end}. Halting load.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Historical Data Backfill ETL")
    parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    asyncio.run(load_historical_data(args.start, args.end))