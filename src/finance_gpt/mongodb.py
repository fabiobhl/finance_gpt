from pymongo.mongo_client import MongoClient

from finance_gpt.news_api import NewsArticle
from dataclasses import asdict


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
        
        
if __name__ == "__main__":
    from finance_gpt.structures import Symbol
    from datetime import datetime
    from finance_gpt.news_api import GPTSentiment
    
    news = NewsArticle(
        company=Symbol("Amazon"),
        url="asdfa",
        title="stasdf",
        text="adfas",
        date=datetime.now(),
        article_type="testa",
        gpt_sentiment=GPTSentiment(-1),
        gpt_verdict="asfasf"
    )
    
    mgdb = MongoDBWrapper()
    
    mgdb.add_news_article(news)
    
    mgdb