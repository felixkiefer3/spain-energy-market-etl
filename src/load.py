import sqlite3
import pandas as pd

def get_last_timestamp(table_name: str, db_name: str = 'energy_data.db') -> str:
    """
    Retrieves the most recent timestamp from the specified database table.
    
    Used to determine the starting point for incremental data loads (Delta Load).
    If the table or database does not exist, it gracefully catches the exception
    and returns None, triggering a full initial load.
    
    Args:
        table_name (str): The name of the table to query.
        db_name (str): The SQLite database filename. Defaults to 'energy_data.db'.
        
    Returns:
        str: The maximum timestamp found, or None if the table is empty/missing.
    """
    try:
        conn = sqlite3.connect(db_name)
        last_date = pd.read_sql(f"SELECT MAX(timestamp) FROM {table_name}", conn).iloc[0, 0]
        conn.close()
        return last_date
    except Exception:
        return None

def load_data(df: pd.DataFrame, table_name: str, db_name: str = 'energy_data.db'):
    """
    Appends a dataframe to the specified SQLite database table.
    
    Args:
        df (pd.DataFrame): The transformed and validated dataframe to load.
        table_name (str): The destination table name.
        db_name (str): The SQLite database filename. Defaults to 'energy_data.db'.
    """
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()