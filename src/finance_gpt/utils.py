import os
import json
from enum import Enum
from finance_gpt import TOP_LEVEL_DIR


def load_credentials() -> dict:
    """Load credentials from credentials.json file."""
    
    credentials_path = os.path.join(TOP_LEVEL_DIR, "credentials.json")
    try:
        with open(credentials_path) as f:
            credentials = json.load(f)    
    except Exception:
        print("Error loading credentials.json file.")
    
    return credentials

def load_tickers() -> list[str]:
    """Loads all tickers from the tickers.json file."""
    tickers_path = os.path.join(TOP_LEVEL_DIR, "tickers.json")
    with open(tickers_path) as f:
        tickers = json.load(f)
    
    return tickers


if __name__ == "__main__":
    credentials = load_credentials()
    print(credentials)