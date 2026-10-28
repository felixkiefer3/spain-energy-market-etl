import pandas as pd
import pandera.pandas as pa

from src.config import TECH_IDS

def transform_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes raw price data.
    
    Args:
        df (pd.DataFrame): Raw price dataframe from the API.
        
    Returns:
        pd.DataFrame: Cleaned dataframe with standardized columns and UTC timestamps.
    """
    df = df.drop_duplicates(subset=['datetime']).copy()
    df_clean = df[['value', 'datetime']].copy()
    df_clean = df_clean.rename(columns={'value': 'price_eur_mwh', 'datetime': 'timestamp'})
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    return df_clean

def transform_generation_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw generation data (already pre-filtered by geographic region at extraction).
    
    Args:
        df (pd.DataFrame): Raw generation dataframe from the API.
        
    Returns:
        pd.DataFrame: Cleaned dataframe with standardized columns and UTC timestamps.
    """
    df_clean = df[['value', 'datetime_utc', 'technology']].copy()
    df_clean = df_clean.rename(columns={'value': 'generation_mwh', 'datetime_utc': 'timestamp'})
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    return df_clean

def handle_anomalies(df: pd.DataFrame, col: str = 'price_eur_mwh', threshold: float = 6.0) -> pd.DataFrame:
    """
    Detects and resolves anomalous data spikes using the Z-score method.
    
    Identifies values deviating from the mean by more than the specified threshold
    and replaces them using linear interpolation.
    
    Args:
        df (pd.DataFrame): The dataframe containing the target column.
        col (str): The column name to check for anomalies.
        threshold (float): The Z-score threshold for outlier detection.
        
    Returns:
        pd.DataFrame: The dataframe with interpolated outliers.
    """
    mean_val = df[col].mean()
    std_val = df[col].std()
    
    if pd.isna(std_val) or std_val == 0:
        return df
        
    z_scores = ((df[col] - mean_val) / std_val).abs()
    
    df.loc[z_scores > threshold, col] = None
    df[col] = df[col].interpolate(method='linear').ffill().bfill()
    
    return df

def create_master_table(df_price: pd.DataFrame, df_gen: pd.DataFrame) -> pd.DataFrame:
    """
    Merges price and generation data, enforces schema completeness, 
    applies anomaly detection, and validates bounds.
    """
    df_gen_pivot = df_gen.pivot(index='timestamp', columns='technology', values='generation_mwh').reset_index()
    df_gen_pivot.columns.name = None 
    
    for tech in TECH_IDS.keys():
        if tech not in df_gen_pivot.columns:
            df_gen_pivot[tech] = float('nan')
    
    df_master = pd.merge(df_price, df_gen_pivot, on='timestamp', how='outer')
    df_master = df_master.sort_values('timestamp').reset_index(drop=True)
    
    df_master['price_eur_mwh'] = df_master['price_eur_mwh'].ffill()
    df_master = df_master.dropna(subset=['price_eur_mwh']).reset_index(drop=True)
    
    df_master = handle_anomalies(df_master)
    
    schema_dict = {
        "timestamp": pa.Column(pd.DatetimeTZDtype(tz="UTC"), nullable=False, coerce=True),
        "price_eur_mwh": pa.Column(float, checks=pa.Check.ge(-500.0), nullable=False)
    }
    
    # Dynamically enforce physical limits based on technology type
    for tech in TECH_IDS.keys():
        if tech == 'hydro':
            schema_dict[tech] = pa.Column(float, nullable=True)
        else:
            schema_dict[tech] = pa.Column(float, checks=pa.Check.ge(0.0), nullable=True)
            
    schema = pa.DataFrameSchema(schema_dict)
    
    return schema.validate(df_master)