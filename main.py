import pandas as pd
from src.extract import extract_indicator_data
from src.transform import transform_price_data, transform_generation_data, create_master_table
from src.load import load_data
from src.config import TECH_IDS

if __name__ == "__main__":
    start = '2026-10-01T00:00:00'
    end = '2026-10-02T00:00:00'
    
    print("1. Extracting wholesale electricity price...")
    df_price_raw = extract_indicator_data('600', start, end)
    df_price_clean = transform_price_data(df_price_raw)
    
    print("2. Extracting generation data by technology...")
    all_generation = []
    
    for tech, ind_id in TECH_IDS.items():
        print(f"   -> Extracting {tech}...")
        try:
            df_raw = extract_indicator_data(ind_id, start, end)
            if not df_raw.empty:
                df_raw['technology'] = tech
                all_generation.append(df_raw)
        except Exception as e:
            print(f"   [!] Failed to extract {tech} (ID {ind_id}): {e}")
            
    if all_generation:
        df_gen_combined = pd.concat(all_generation, ignore_index=True)
        df_gen_clean = transform_generation_data(df_gen_combined)
        
        print("3. Creating master table...")
        df_master = create_master_table(df_price_clean, df_gen_clean)
        
        print("4. Loading master data into database...")
        load_data(df_master, 'energy_master')
    
    print("Pipeline execution completed successfully!")