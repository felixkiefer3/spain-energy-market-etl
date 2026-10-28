import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock
from src.extract import fetch_indicator

@pytest.mark.asyncio
async def test_fetch_indicator_returns_dataframe():
    """
    Tests the asynchronous data extraction function by mocking the HTTP session.
    
    Verifies that the function correctly parses a simulated JSON response from 
    the API and returns a properly structured pandas DataFrame, without making 
    actual network requests.
    """
    mock_session = MagicMock()
    mock_response = AsyncMock()
    
    mock_response.json.return_value = {
        'indicator': {
            'values': [{'value': 120.5, 'datetime': '2026-10-01T00:00:00Z'}]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Simulate entering the 'async with' context manager
    mock_session.get.return_value.__aenter__.return_value = mock_response

    df = await fetch_indicator(mock_session, '600', '2026-10-01', '2026-10-02')

    assert isinstance(df, pd.DataFrame), "Did not return a pandas DataFrame."
    assert not df.empty, "DataFrame is empty."
    assert df.iloc[0]['value'] == 120.5, "Value extraction failed."