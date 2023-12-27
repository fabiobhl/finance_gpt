from finance_gpt.utils import load_credentials, Company
from enum import Enum
from dataclasses import dataclass
import datetime
import requests

class GPTSentiment(Enum):
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1

@dataclass
class NewsArticle:
    # raw data
    company: Company
    url: str
    title: str
    text: str
    date: datetime.datetime
    article_type: str
    
    # sentiment analysis
    gpt_sentiment: GPTSentiment
    gpt_verdict: str
    
    @classmethod
    def from_dict(cls, data: dict, ticker: str = None):
        """Creates a NewsArticle from a dictionary."""
        
        # parse date
        date_object = datetime.datetime.strptime(data["date"], '%a, %d %b %Y %H:%M:%S %z')
        
        return cls(
            company=Company[ticker],
            url=data["news_url"],
            title=data["title"],
            text=data["text"],
            date=date_object,
            article_type=data["type"],
            gpt_sentiment=None,
            gpt_verdict=None,
        )        

class NewsApi():
    
    def __init__(self):
        # load in the api key
        self._load_api_key()
        # endpoint
        self.url = "https://stocknewsapi.com/api/v1"

    def _load_api_key(self):
        """Loads the API key from the credentials file."""
        try:
            creds = load_credentials()
        except:
            raise Exception("Not able to load in credentials, please make sure you have a credentials file with the correct format.")
        
        self.api_key = creds["stocknewsapi"]["key"]
    
    def get_news(self, ticker: str) -> list[NewsArticle]:
        params = {
            "tickers": ticker,
            "items": 3,
            "page": 1,
            "token": self.api_key,
        }
        response = requests.get(self.url, params=params)
        
        data = response.json()["data"]

        return [NewsArticle.from_dict(news_dict, ticker=ticker) for news_dict in data]
            
if __name__ == "__main__":
    news_api = NewsApi()
    news = news_api.get_news("AMZN")
    print(news)