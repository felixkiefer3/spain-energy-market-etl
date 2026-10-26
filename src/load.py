import sqlite3
import pandas as pd

def get_last_timestamp(table_name: str, db_name: str = 'energy_data.db') -> str:
    try:
        conn = sqlite3.connect(db_name)
        last_date = pd.read_sql(f"SELECT MAX(timestamp) FROM {table_name}", conn).iloc[0, 0]
        conn.close()
        return last_date
    except Exception:
        return None

def load_data(df: pd.DataFrame, table_name: str, db_name: str = 'energy_data.db'):
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()