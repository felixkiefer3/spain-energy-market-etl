import pandas as pd

def transform_price_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=['datetime']).copy()
    
    df_clean = df[['value', 'datetime']].copy()
    df_clean = df_clean.rename(columns={'value': 'price_eur_mwh', 'datetime': 'timestamp'})
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    return df_clean
def transform_generation_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['geo_id'] == 8741].copy()
    df_clean = df[['value', 'datetime_utc', 'technology']].copy()
    df_clean = df_clean.rename(columns={'value': 'generation_mwh', 'datetime_utc': 'timestamp'})
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    return df_clean

def create_master_table(df_price: pd.DataFrame, df_gen: pd.DataFrame) -> pd.DataFrame:
    """Pivots generation data, merges with price data, and fills missing values."""
    df_gen_pivot = df_gen.pivot(index='timestamp', columns='technology', values='generation_mwh').reset_index()
    df_gen_pivot.columns.name = None 
    
    df_master = pd.merge(df_price, df_gen_pivot, on='timestamp', how='outer')
    df_master = df_master.sort_values('timestamp').reset_index(drop=True)
    
    df_master['price_eur_mwh'] = df_master['price_eur_mwh'].ffill()
    
    df_master = df_master.dropna(subset=['price_eur_mwh']).reset_index(drop=True)
    
    return df_master