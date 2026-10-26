import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and formats the raw DataFrame."""
    df_clean = df[['value', 'datetime']].copy()
    df_clean = df_clean.rename(columns={'value': 'price_eur_mwh', 'datetime': 'timestamp'})
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    
    return df_clean