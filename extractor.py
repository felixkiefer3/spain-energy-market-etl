import os
import requests
import pandas as pd
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# Configuration
API_KEY = os.getenv('ESIOS_TOKEN')
HEADERS = {
    'Accept': 'application/json; application/vnd.esios-api-v2+json',
    'x-api-key': API_KEY
}
BASE_URL = 'https://api.esios.ree.es/indicators'

def extract_indicator_data(indicator_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Extracts data from ESIOS API and returns a pandas DataFrame."""
    url = f"{BASE_URL}/{indicator_id}"
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status() # Fails script if HTTP error occurs
    
    # Parse JSON and extract values
    data = response.json()
    values = data['indicator']['values']
    
    # Transform into a DataFrame for easier manipulation
    df = pd.DataFrame(values)
    return df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and formats the raw DataFrame."""
    # Keep only relevant columns
    df_clean = df[['value', 'datetime']].copy()
    
    # Rename to SQL standards (snake_case)
    df_clean = df_clean.rename(columns={'value': 'price_eur_mwh', 'datetime': 'timestamp'})
    
    # Convert string to standard datetime object (UTC)
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], utc=True)
    
    return df_clean

def load_data(df: pd.DataFrame, db_name: str = 'energy_data.db'):
    """Loads the DataFrame into a local SQLite database."""
    # Create connection to the local database file
    conn = sqlite3.connect(db_name)
    
    # Insert data into a table named 'wholesale_price'
    df.to_sql('wholesale_price', conn, if_exists='replace', index=False)
    
    conn.close()

if __name__ == "__main__":
    start = '2026-10-01T00:00:00'
    end = '2026-10-02T00:00:00'
    
    print("Extracting wholesale electricity price...")
    df_raw = extract_indicator_data('600', start, end)
    
    print("Transforming data...")
    df_clean = transform_data(df_raw)
    
    print("Loading data into database...")
    load_data(df_clean)
    
    print("Pipeline execution completed successfully!")