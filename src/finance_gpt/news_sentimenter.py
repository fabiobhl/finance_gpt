import datetime
from finance_gpt import setup_logger
from finance_gpt.scheduler import SentimentScheduler
from finance_gpt.news_api import NewsApi, NewsArticle
from finance_gpt.gpt import GPT
from finance_gpt.utils import load_tickers
from finance_gpt.mongodb import MongoDBWrapper

logger = setup_logger(__name__)

if __name__ == "__main__":
    
    # setup
    logger.debug("Starting News Sentimenter.")
    try:
        # timer
        scheduler = SentimentScheduler(interval=15)
        # news api
        news_api = NewsApi()
        # sentiment model
        gpt = GPT()
        # mongodb wrapper
        db = MongoDBWrapper()
        # load in all tickers to look at
        tickers = load_tickers()
    except:
        logger.exception("Failed to setup news sentimenter")
        exit()
    
    # main loop
    try:
        while True:
            # load news
            logger.debug("Loading news.")
            # TODO change to last 15 min
            news = news_api.get_news(tickers, time_interval_str="last30min")
                        
            # load in all urls from this day minutes
            processed_urls = db.get_urls(time_frame=datetime.timedelta(days=1))
            
            # sentiment news that are not yet processed
            logger.debug("Sentimenting news.")
            for news_dict in news:
                if news_dict["news_url"] not in processed_urls:
                    # copy the news_dict
                    news_dict_copy = news_dict.copy()
                    news_dict_copy["gpt_sentiment"] = {}
                    news_dict_copy["gpt_verdict"] = {}
                                        
                    # sentiment article for every relevant company
                    for ticker in news_dict["tickers"]:
                        if ticker in tickers:
                            # convert news dict to news article
                            news_article = NewsArticle.from_dict(news_dict, ticker)
                            # sentiment it using chat gpt
                            gpt.get_sentiment(news_article, term="short")
                            
                            # save sentiment in copy
                            news_dict_copy["gpt_sentiment"][ticker] = news_article.gpt_sentiment.value
                            news_dict_copy["gpt_verdict"][ticker] = news_article.gpt_verdict
                    
                    # save them in the database
                    db.add_news_articles([news_dict_copy])
            
            # sleep until next interval
            logger.debug("Sleeping until next interval")
            scheduler.sleep()
    
    except:
        logger.exception("Failed in main loop of news sentimenter")