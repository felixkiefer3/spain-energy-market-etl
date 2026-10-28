import pandas as pd
import numpy as np
import pytest
from pandera.errors import SchemaError

from src.transform import handle_anomalies
from src.transform import create_master_table


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

def test_schema_enforcement_missing_columns():
    """Verifies that omitted technologies are injected as float64 (NaN)."""
    df_price = pd.DataFrame({
        'timestamp': [pd.Timestamp('2024-01-01 00:00:00', tz='UTC')],
        'price_eur_mwh': [50.0]
    })
    
    df_gen = pd.DataFrame({
        'timestamp': [pd.Timestamp('2024-01-01 00:00:00', tz='UTC')],
        'technology': ['wind'],
        'generation_mwh': [100.5]
    })
    
    df_master = create_master_table(df_price, df_gen)
    
    assert 'solar' in df_master.columns
    assert np.isnan(df_master['solar'].iloc[0])
    assert df_master['solar'].dtype == 'float64'

def test_hydro_allows_negative_generation():
    """Verifies that the schema tolerates negative values exclusively for hydro."""
    df_price = pd.DataFrame({
        'timestamp': [pd.Timestamp('2024-01-01 00:00:00', tz='UTC')],
        'price_eur_mwh': [50.0]
    })
    
    df_gen_hydro = pd.DataFrame({
        'timestamp': [pd.Timestamp('2024-01-01 00:00:00', tz='UTC')],
        'technology': ['hydro'],
        'generation_mwh': [-250.0] 
    })
    
    df_master = create_master_table(df_price, df_gen_hydro)
    assert df_master['hydro'].iloc[0] == -250.0

    df_gen_wind = pd.DataFrame({
        'timestamp': [pd.Timestamp('2024-01-01 00:00:00', tz='UTC')],
        'technology': ['wind'],
        'generation_mwh': [-10.0]
    })
    
    with pytest.raises(SchemaError):
        create_master_table(df_price, df_gen_wind)