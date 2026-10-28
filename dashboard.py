import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

st.set_page_config(page_title="Energy Market Dashboard", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Connects to SQLite, loads the master table, and caches the result 
    to optimize dashboard performance.
    """
    with sqlite3.connect('energy_data.db') as conn:
        df = pd.read_sql_query("SELECT * FROM energy_master ORDER BY timestamp", conn)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def main():
    """
    Renders the Streamlit application layout and plots, implementing 
    date filtering and an interactive dual-axis chart.
    """
    st.title("Energy Market Dashboard")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data found in the database. Run historical_load.py first.")
        return

    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    default_start = max_date - timedelta(days=30)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_dates = st.date_input(
            "Date Range",
            value=(default_start, max_date),
            min_value=min_date,
            max_value=max_date
        )

    if len(selected_dates) != 2:
        st.stop()
        
    start_date, end_date = selected_dates
    
    mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
    df_filtered = df.loc[mask].copy()

    gen_columns = [col for col in df_filtered.columns if col not in ['timestamp', 'price_eur_mwh']]
    df_filtered['total_generation'] = df_filtered[gen_columns].sum(axis=1)

    tech_options = ['total_generation'] + gen_columns
    selected_tech = st.selectbox("Select Generation Source", options=tech_options, index=0)

    st.subheader(f"Price vs {selected_tech}")
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_combo.add_trace(
        go.Scatter(
            x=df_filtered['timestamp'], y=df_filtered[selected_tech], 
            name=selected_tech, fill='tozeroy', opacity=0.3, line=dict(color='blue')
        ),
        secondary_y=False,
    )
    
    fig_combo.add_trace(
        go.Scatter(
            x=df_filtered['timestamp'], y=df_filtered['price_eur_mwh'], 
            name="Price", line=dict(color='red', width=2)
        ),
        secondary_y=True,
    )
    
    fig_combo.update_yaxes(title_text="Generation (MWh)", secondary_y=False)
    fig_combo.update_yaxes(title_text="Price (EUR/MWh)", secondary_y=True)
    fig_combo.update_layout(hovermode="x unified")
    
    st.plotly_chart(fig_combo, width='stretch')

    st.subheader("Peninsular Generation Mix")
    fig_gen = px.area(
        df_filtered, 
        x='timestamp', 
        y=gen_columns,
        labels={'value': 'Generation (MWh)', 'timestamp': 'Time', 'variable': 'Technology'}
    )
    st.plotly_chart(fig_gen, width='stretch')

if __name__ == "__main__":
    main()