from dataclasses import asdict
import datetime
from pymongo.mongo_client import MongoClient
from finance_gpt.news_api import NewsArticle
from finance_gpt.structures import Symbol




class MongoDBWrapper():
    
    def __init__(self) -> None:
        self.client = MongoClient("mongodb://localhost:27017")
        
    def add_news_article(self, news_article: NewsArticle) -> None:
        """Adds a game state to the database"""
        
        # get the database and collection
        db = self.client["news"]
        collection = db[news_article.company.name]
        
        # insert the game state
        collection.insert_one(asdict(news_article, dict_factory=NewsArticle.dict_factory_fun))
        
    def get_urls(self, symbol: Symbol, time_frame: datetime.timedelta) -> list[str]:
        """Get all urls from one symbol and a certain time frame"""
        
        # get the database and collection
        db = self.client["news"]
        collection = db[symbol.name]
        
        # target date is today
        target_date = datetime.datetime.now()
        target_date = datetime.date(year=target_date.year, month=target_date.month, day=target_date.day)
        
        urls = []
        for entry in collection.find({"date": {"$gte": (target_date-time_frame).isoformat()}}):
            urls.append(entry["url"])
            
        return urls
        
if __name__ == "__main__":
    from finance_gpt.news_api import GPTSentiment
    
    mgdb = MongoDBWrapper()
    
    print(mgdb.get_urls(symbol=Symbol("Amazon"), time_frame=datetime.timedelta(days=7)))