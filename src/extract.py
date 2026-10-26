import os
import asyncio
import aiohttp
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    'Accept': 'application/json; application/vnd.esios-api-v2+json',
    'x-api-key': os.getenv('ESIOS_TOKEN')
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_indicator(session: aiohttp.ClientSession, indicator_id: str, start: str, end: str) -> pd.DataFrame:
    url = f"https://api.esios.ree.es/indicators/{indicator_id}?start_date={start}&end_date={end}"
    
    async with session.get(url, headers=HEADERS) as response:
        response.raise_for_status()
        data = await response.json()
        values = data.get('indicator', {}).get('values', [])
        return pd.DataFrame(values) if values else pd.DataFrame()

async def extract_all_data(price_id: str, tech_ids: dict, start: str, end: str) -> tuple:
    async with aiohttp.ClientSession() as session:
        price_task = asyncio.create_task(fetch_indicator(session, price_id, start, end))
        
        gen_tasks = {
            tech: asyncio.create_task(fetch_indicator(session, ind_id, start, end))
            for tech, ind_id in tech_ids.items()
        }
        
        df_price = await price_task
        
        generation_results = []
        for tech, task in gen_tasks.items():
            df_tech = await task
            if not df_tech.empty:
                df_tech['technology'] = tech
                generation_results.append(df_tech)
                
        df_gen_combined = pd.concat(generation_results, ignore_index=True) if generation_results else pd.DataFrame()
        
        return df_price, df_gen_combined