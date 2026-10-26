import pandas as pd
from datetime import datetime, timezone
from src.extract import extract_indicator_data
from src.transform import transform_price_data, transform_generation_data, create_master_table
from src.load import load_data, get_last_timestamp
from src.config import TECH_IDS
from src.logger import setup_logger

logger = setup_logger()

if __name__ == "__main__":
    last_date = get_last_timestamp('energy_master')
    
    if last_date:
        start = (pd.to_datetime(last_date) + pd.Timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
        logger.info(f"Incremental load starting from {start}")
    else:
        start = '2026-10-01T00:00:00'
        logger.info("Initial full load")

    end = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    
    logger.info("Extracting wholesale electricity price...")
    df_price_raw = extract_indicator_data('600', start, end)
    df_price_clean = transform_price_data(df_price_raw)
    
    logger.info("Extracting generation data by technology...")
    all_generation = []
    
    for tech, ind_id in TECH_IDS.items():
        logger.info(f"Extracting {tech}...")
        try:
            df_raw = extract_indicator_data(ind_id, start, end)
            if not df_raw.empty:
                df_raw['technology'] = tech
                all_generation.append(df_raw)
        except Exception as e:
            logger.error(f"Failed to extract {tech} (ID {ind_id}): {e}")
            
    if all_generation:
        df_gen_combined = pd.concat(all_generation, ignore_index=True)
        df_gen_clean = transform_generation_data(df_gen_combined)
        
        logger.info("Creating master table...")
        df_master = create_master_table(df_price_clean, df_gen_clean)
        
        logger.info("Loading master data into database...")
        load_data(df_master, 'energy_master')
    
    logger.info("Pipeline execution completed successfully!")