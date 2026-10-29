# Energy Market ETL Pipeline & Dashboard

A production-ready, asynchronous ETL pipeline that extracts historical and incremental electricity market data (Prices and Generation Mix) from the ESIOS API (Red Eléctrica de España), processes it with strict data validation, and visualizes it through an interactive Streamlit dashboard.

## Features

- **Asynchronous Extraction:** Uses `aiohttp` and `asyncio` for concurrent API requests, significantly reducing data fetch times.
- **Stateful Historical Backfill:** Time-chunked historical loading with resume capability (checkpointing) to prevent data duplication and recover cleanly from network failures.
- **Robust Transformation & Validation:** 
  - Dynamic schema enforcement injecting `NaN` for missing API data to ensure database schema stability.
  - Granular validation using `Pandera`, enforcing OMIE market limits and allowing negative physical values exclusively for pumped-storage hydroelectricity.
  - Implements a 1-hour lookback window during incremental loads to provide context for forward-filling missing 15-minute price intervals.
- **Interactive Dashboard:** Dual-axis Streamlit and Plotly dashboard with date filtering and dynamic technology selection.

## Tech Stack

- **Language:** Python 3.10+
- **Data Processing:** Pandas, Pandera
- **Extraction & Orchestration:** Aiohttp, Asyncio, Tenacity
- **Database:** SQLite
- **Visualization:** Streamlit, Plotly

## Setup and Usage

You can run this project using Docker (recommended for a quick start without local dependencies) or via a local Python environment.

### Option A: Docker (Quick Start)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/felixkiefer3/spain-energy-market-etl.git
   cd spain-energy-market-etl
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory and add your ESIOS API token:
   ```ini
   ESIOS_TOKEN=your_api_token_here
   INITIAL_START_DATE=2024-01-01T00:00:00Z
   ```
   *(You can change the initial date to a different one).*

3. **Build the image:**
   > **Note:** Ensure Docker Desktop (or the Docker daemon) is running.
   ```bash
   docker build -t spain-energy-market-etl .
   ```

4. **Run the Application:**
   Keep the SQLite database synced with your local filesystem via volume mapping. Use `${PWD}` for Windows PowerShell or `$(pwd)` for Linux/macOS Bash.

   - **Incremental ETL Load:**
     ```bash
     # Windows (PowerShell)
     docker run --env-file .env -v ${PWD}:/app spain-energy-market-etl python main.py
     
     # Linux/macOS (Bash)
     docker run --env-file .env -v $(pwd):/app spain-energy-market-etl python main.py
     ```
   
   - **Launch Dashboard (Accessible at http://localhost:8501):**
     ```bash
     # Windows (PowerShell)
     docker run -p 8501:8501 --env-file .env -v ${PWD}:/app spain-energy-market-etl streamlit run dashboard.py
     
     # Linux/macOS (Bash)
     docker run -p 8501:8501 --env-file .env -v $(pwd):/app spain-energy-market-etl streamlit run dashboard.py
     ```

---

### Option B: Local Python Environment (Development)

1. **Clone and activate a virtual environment:**
   ```bash
   git clone https://github.com/felixkiefer3/spain-energy-market-etl.git
   cd spain-energy-market-etl
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Install dependencies and configure `.env`:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Create the `.env` file as shown in the Docker steps).*

3. **Execute:**
   ```bash
   # Historical Backfill (downloads large volumes of historical data)
   python historical_load.py --start 2024-01-01 --end 2026-10-01
   
   # Incremental Load (fetches only the most recent data)
   python main.py
   
   # Dashboard (launches local web interface)
   streamlit run dashboard.py
   ```

## Scheduling & Automation

To run this pipeline as a continuous ETL process, schedule `main.py` to execute automatically at regular intervals.

### Windows (Task Scheduler):
Run the included `setup_task.bat` file to schedule the pipeline to run every 15 minutes:
```cmd
schtasks /create /tn "Spain_Energy_Market_ETL" /tr "%~dp0.venv\Scripts\python.exe %~dp0main.py" /sc minute /mo 15
```

### Linux/macOS (Cron):
Add the following line to your crontab (`crontab -e`) to execute every 15 minutes:
```bash
*/15 * * * * cd /path/to/spain-energy-market-etl && .venv/bin/python main.py
```

## Testing

The project includes unit tests to verify business logic and schema enforcement (e.g., dynamic column injection, hydro limits). Tests run automatically via GitHub Actions on every push to the `main` branch.

To run tests locally:
```bash
pytest tests/
```