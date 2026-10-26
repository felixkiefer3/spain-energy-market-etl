import os
import requests
import pandas as pd
from dotenv import load_dotenv

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

if __name__ == "__main__":
    # Define time range
    start = '2026-10-01T00:00:00'
    end = '2026-10-02T00:00:00'
    
    print("Extracting wholesale electricity price (ID 600)...")
    df_price = extract_indicator_data('600', start, end)
    
    # Display the first 5 rows of the extracted tabular data
    print(df_price[['value', 'datetime']].head())