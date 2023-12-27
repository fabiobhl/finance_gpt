import os
import json
from finance_gpt import TOP_LEVEL_DIR


def load_credentials() -> dict:
    """Load credentials from credentials.json file."""
    
    credentials_path = os.path.join(TOP_LEVEL_DIR, "credentials.json")
    with open(credentials_path) as f:
        credentials = json.load(f)    
    
    return credentials


if __name__ == "__main__":
    credentials = load_credentials()
    print(credentials)