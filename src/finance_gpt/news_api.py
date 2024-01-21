# standard libraries
from enum import Enum
from dataclasses import dataclass
import datetime
import pytz
import requests
# finance_gpt imports
from finance_gpt.utils import load_credentials, load_tickers
from finance_gpt.structures import Symbol

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
            gpt_sentiment=None,
            gpt_verdict=None,
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
    
    def get_news(self, ticker: str) -> list[NewsArticle]:
        params = {
            "tickers": ticker,
            "items": 50,
            "sortby": "rank",
            "days": 1,
            "token": self.api_key,
        }
        response = requests.get(self.url, params=params)
        
        data = response.json()["data"]

        processed_data = [NewsArticle.from_dict(news_dict, ticker=ticker) for news_dict in data]
        
        final_data = []
        for news in processed_data:
            time_dt = abs((news.date - pytz.timezone("Europe/Zurich").localize(datetime.datetime.now())).total_seconds())
            if time_dt < datetime.timedelta(days=1).total_seconds():
                final_data.append(news)
        
        return final_data

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
    news = news_api.get_news("AMZN")
    print(news)