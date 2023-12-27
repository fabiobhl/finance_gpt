import json
from finance_gpt.utils import load_credentials
import datetime
import requests
from tqdm import tqdm

def download_data(ticker: str):
    """Download all news data from one ticker"""
    
    all_data = []
    
    api_key = load_credentials()["stocknewsapi"]["key"]
    
    start_date = datetime.datetime(2019, 3, 1)
    day_step = datetime.timedelta(days=7)

    # Iterate over all days since start date
    current_date = start_date
    with tqdm(total=251) as pbar:
        while True:
            to_date = current_date + datetime.timedelta(days=6)
            date_string1 = current_date.strftime("%m%d%Y")
            date_string2 = to_date.strftime("%m%d%Y")
            date_string = date_string1 + "-" + date_string2

            # get data
            page=1
            while True:
                params = {
                    "tickers": ticker,
                    "date": date_string,
                    "items": 100,
                    "page": page,
                    "token": api_key,
                }
                response = requests.get("https://stocknewsapi.com/api/v1", params=params)
                data = response.json()["data"]
                    
                all_data += data
                
                if page >= response.json()["total_pages"]:
                    break
                
                page += 1
            
            # termination check
            if to_date >= datetime.datetime.now():
                break
            
            # step one day
            current_date += day_step
            
            # update progress bar
            pbar.update(1)
    
    with open(f"/Users/fabio/git/finance_gpt/data/news/{ticker}.json", 'w') as json_file:
        json.dump(all_data, json_file, indent=2)
    
def download_100():
    with open("/Users/fabio/git/finance_gpt/data/tickers.json") as user_file:
        tickers = json.load(user_file)
    
    for ticker in tqdm(tickers, unit="ticker"):
        download_data(ticker)


    
if __name__ == "__main__":
    download_100()