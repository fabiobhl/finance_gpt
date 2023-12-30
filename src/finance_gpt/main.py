from finance_gpt.scheduler import Scheduler
from finance_gpt.news_api import load_all_news
from finance_gpt.gpt import GPT
from finance_gpt.portfolio_manager import PortfolioManager
from finance_gpt.structures import Symbol
import pandas as pd

AMOUNT_OF_STOCKS = 6

if __name__ == "__main__":
    
    # setup
    # timer
    scheduler = Scheduler()
    # sentiment model
    gpt = GPT()
    # portfolio manager
    pm = PortfolioManager()
    
    # main loop
    while True:
        
        # sleep until market opens (10 minutes before)
        scheduler.sleep(minutes=30)
        
        # load news
        news = load_all_news()
        
        # sentiment them with chat gpt
        for key, value in news.items():
            for news_article in value:
                gpt.get_sentiment(news_article, term="short")
        
        # calculate sentiment score
        scores = {}
        for key, value in news.items():
            scores[key] = 0
            counter = 0
            for news_article in value:
                scores[key] += news_article.gpt_sentiment.value
                counter += 1
                
            if counter == 0:
                del scores[key]
            else:
                scores[key] /= counter
        
        # get the best stocks (AMOUNT_OF_STOCKS)
        score_df = pd.DataFrame.from_dict(scores, orient="index", columns=["score"])
        score_df["absolute_score"] = abs(score_df["score"])
        sorted_score_df = score_df.sort_values(by="absolute_score", ascending=False)
        new_stocks = sorted_score_df.iloc[:AMOUNT_OF_STOCKS, :]
        
        # cut the scores to have a absolute value bigger than 0.7
        new_stocks = new_stocks[new_stocks["absolute_score"] >= 0.7]
        
        # create the portfolio
        new_portfolio = pm.create_portfolio(new_stocks)
        
        # wait for markets to open
        scheduler.sleep_until_market_open()
        
        # update the portfolio accordingly
        pm.update(new_portfolio=new_portfolio)
        
        