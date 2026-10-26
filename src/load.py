import sqlite3
import pandas as pd

def load_data(df: pd.DataFrame, db_name: str = 'energy_data.db'):
    """Loads the DataFrame into a local SQLite database."""
    conn = sqlite3.connect(db_name)
    df.to_sql('wholesale_price', conn, if_exists='replace', index=False)
    conn.close()