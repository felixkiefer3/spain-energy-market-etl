import pandas as pd
import pytest
from src.transform import handle_anomalies

def test_handle_anomalies_removes_outliers():
    """
    Tests the anomaly detection and linear interpolation logic.
    
    Verifies that a synthetic extreme outlier is correctly identified, 
    removed, and replaced with an accurate linearly interpolated value 
    without leaving any nulls in the dataset.
    """
    data = {'price_eur_mwh': [50.0, 52.0, 51.0, 50.5, 51.5, 49.5, 50.0, 51.0, 52.0, 999.0, 50.5, 51.5]}
    df = pd.DataFrame(data)
    
    df_clean = handle_anomalies(df, col='price_eur_mwh', threshold=3.0)
    
    assert df_clean['price_eur_mwh'].max() < 100.0, "Anomalous value was not removed."
    assert not df_clean['price_eur_mwh'].isna().any(), "Null values found after interpolation."
    
    assert df_clean.iloc[9]['price_eur_mwh'] == 51.25, "Linear interpolation failed."