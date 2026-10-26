import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

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
    response.raise_for_status()
    
    data = response.json()
    values = data['indicator']['values']
    
    return pd.DataFrame(values)