from src.extract import extract_indicator_data
from src.transform import transform_data
from src.load import load_data

if __name__ == "__main__":
    start = '2026-10-01T00:00:00'
    end = '2026-10-02T00:00:00'
    
    print("1. Extracting wholesale electricity price...")
    df_raw = extract_indicator_data('600', start, end)
    
    print("2. Transforming data...")
    df_clean = transform_data(df_raw)
    
    print("3. Loading data into database...")
    load_data(df_clean)
    
    print("Pipeline execution completed successfully!")