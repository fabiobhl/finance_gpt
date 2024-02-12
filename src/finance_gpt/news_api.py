# standard libraries
from enum import Enum
from dataclasses import dataclass
import datetime
import pytz
import requests
# finance_gpt imports
from finance_gpt.utils import load_credentials, load_tickers, setup_logger
from finance_gpt.structures import Symbol

logger = setup_logger(__name__)

class GPTSentiment(Enum):
    YES = 1
    UNKNOWN = 0
    NO = -1

@dataclass
class NewsArticle:
    # raw data
    company: Symbol
    url: str
    title: str
    text: str
    date: datetime.datetime
    article_type: str
    source_name: str
    pre_sentiment: str
    
    # sentiment analysis
    gpt_sentiment: GPTSentiment
    gpt_verdict: str
    
    @classmethod
    def from_dict(cls, data: dict, ticker: str = None):
        """Creates a NewsArticle from a dictionary."""
        
        # parse date
        date_object = datetime.datetime.strptime(data["date"], '%a, %d %b %Y %H:%M:%S %z')
        
        return cls(
            company=Symbol[ticker],
            url=data["news_url"],
            title=data["title"],
            text=data["text"],
            date=date_object,
            article_type=data["type"],
            source_name=data["source_name"],
            pre_sentiment=data["sentiment"],
            gpt_sentiment=None,
            gpt_verdict=None,
        )
        
    @classmethod
    def from_db(cls, data: dict, ticker: str = None):
        """Creates a NewsArticle from a dictionary."""
        
        # parse date
        date_object = datetime.datetime.strptime(data["date"], '%a, %d %b %Y %H:%M:%S %z')
        
        return cls(
            company=Symbol[ticker],
            url=data["news_url"],
            title=data["title"],
            text=data["text"],
            date=date_object,
            article_type=data["type"],
            source_name=data["source_name"],
            pre_sentiment=data["sentiment"],
            gpt_sentiment=GPTSentiment(int(data["gpt_sentiment"][ticker])),
            gpt_verdict=data["gpt_verdict"][ticker],
        ) 
        
    @staticmethod
    def dict_factory_fun(data):
        def convert_value(obj):
            if isinstance(obj, Symbol):
                return obj.name
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, GPTSentiment):
                return obj.name
            else:
                return obj

        return dict((k, convert_value(v)) for k, v in data)

class NewsApi():
    
    def __init__(self):
        # load in the api key
        self.api_key = self._load_api_key()
        # endpoint
        self.url = "https://stocknewsapi.com/api/v1"

    def _load_api_key(self) -> str:
        """Loads the API key from the credentials file."""
        try:
            creds = load_credentials()
            return creds["stocknewsapi"]["key"]
        except:
            raise Exception("Not able to load in credentials, please make sure you have a credentials file with the correct format.")
    
    def get_news(self, tickers: list[str], time_interval_str: str) -> list[dict]:
        
        data = []
        
        for i in range(len(tickers)//50+1):
            # create ticker string
            ticker_str = ""
            for symb in tickers[i*50:(i+1)*50]:
                ticker_str += symb + ","
            
            # get data
            page_number = 1
            done = False
            max_retries = 5
            while not done:
                for _ in range(max_retries):
                    params = {
                        "tickers": ticker_str[:-1],
                        "items": 100,
                        "page": page_number,
                        "date": time_interval_str,
                        "token": self.api_key,
                    }
                    response = requests.get(self.url, params=params)
                    logger.debug(f"response: {response}")
                    
                    if int(response.status_code) != 200:
                        logger.error(f"News data was not able to load, retrying, status_code: {response.status_code}")
                    else:
                        break
                
                new_data = response.json()["data"]
                
                # if new data is empty skip
                if len(new_data) == 0:
                    done = True
                    continue
                
                # get total number of pages
                pages = response.json()["total_pages"]
                
                # add data
                data += new_data
                
                # if data overflowed update page number
                if page_number < pages:
                    page_number += 1
                else:
                    done = True

        return data

def load_all_news() -> dict[str:list[NewsArticle]]:
    """Loads all news from the last 24 hours."""
    
    news_api = NewsApi()
    tickers = load_tickers()
    
    news = {}
    
    for ticker in tickers:
        news[ticker] = news_api.get_news(ticker)
    
    return news
                   
if __name__ == "__main__":
    news_api = NewsApi()
    tickers = load_tickers()
    news = news_api.get_news(tickers=tickers, time_interval_str="last60min")