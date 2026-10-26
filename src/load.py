import sqlite3
import pandas as pd

def load_data(df: pd.DataFrame, table_name: str, db_name: str = 'energy_data.db'):
    """Loads the DataFrame into a local SQLite database table."""
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()