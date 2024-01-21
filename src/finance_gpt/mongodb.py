from dataclasses import asdict
import datetime
from pymongo.mongo_client import MongoClient
from finance_gpt.news_api import NewsArticle
from finance_gpt.structures import Symbol




class MongoDBWrapper():
    
    def __init__(self) -> None:
        self.client = MongoClient("mongodb://localhost:27017")
        
    def add_news_articles(self, news_articles: list[dict]) -> None:
        """Adds a game state to the database"""
        
        # get the database and collection
        db = self.client["news"]
        collection = db["stocknewsapi"]
        
        # insert the game state
        for news_article in news_articles:
            collection.insert_one(news_article)
        
    def get_urls(self, time_frame: datetime.timedelta) -> list[str]:
        """Get all urls from one symbol and a certain time frame"""
        
        # get the database and collection
        db = self.client["news"]
        collection = db["stocknewsapi"]
        
        # target date is now
        target_date = datetime.datetime.now()
        
        urls = []
        for entry in collection.find({"date": {"$gte": (target_date-time_frame).isoformat()}}):
            urls.append(entry["news_url"])
            
        return urls
        
if __name__ == "__main__":
    from finance_gpt.news_api import GPTSentiment
    
    mgdb = MongoDBWrapper()
    
    print(mgdb.get_urls(symbol=Symbol("Amazon"), time_frame=datetime.timedelta(days=7)))