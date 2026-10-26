import os
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    'Accept': 'application/json; application/vnd.esios-api-v2+json',
    'x-api-key': os.getenv('ESIOS_TOKEN')
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_indicator_data(indicator_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    url = f"https://api.esios.ree.es/indicators/{indicator_id}?start_date={start_date}&end_date={end_date}"
    
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    values = data.get('indicator', {}).get('values', [])
    
    return pd.DataFrame(values) if values else pd.DataFrame()