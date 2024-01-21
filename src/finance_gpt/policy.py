import datetime
from finance_gpt.portfolio_manager import Portfolio, PortfolioManager
from finance_gpt.mongodb import MongoDBWrapper
from finance_gpt import setup_logger

import pandas as pd

class Policy():
    
    def __init__(self, name: str, parameters: dict) -> None:
        self.name = name
        self.parameters = parameters
        self.logger = setup_logger(f"Policy-{self.name}")
        self.logger.info(f"Starting up policy: {self.name} with parameters: {self.parameters}")
        
        self.db = MongoDBWrapper()
        self.pm = PortfolioManager()
    
    def get_portfolio(self) -> Portfolio:
        
        AMOUNT_OF_STOCKS = 15
        
        # get the news
        news = self.db.get_news_articles(time_frame=datetime.timedelta(days=1))
        
        # calculate sentiment score
        self.logger.debug("Calculating sentiment score.")
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
        self.logger.debug(f"Getting the {AMOUNT_OF_STOCKS} best stocks.")
        score_df = pd.DataFrame.from_dict(scores, orient="index", columns=["score"])
        score_df["absolute_score"] = abs(score_df["score"])
        sorted_score_df = score_df.sort_values(by="absolute_score", ascending=False)
        new_stocks = sorted_score_df.iloc[:AMOUNT_OF_STOCKS, :]
        self.logger.debug(f"New stocks: {new_stocks}")
        
        # cut the scores to have a absolute value bigger than 0.7
        self.logger.debug("Cutting the scores to have a absolute value bigger than 0.7.")
        new_stocks = new_stocks[new_stocks["absolute_score"] >= 0.7]
        self.logger.debug(f"New stocks: {new_stocks}")
        
        # create the portfolio
        self.logger.debug("Creating the portfolio.")
        new_portfolio = self.pm.create_portfolio(new_stocks)
        self.logger.debug(f"New portfolio: {new_portfolio}")
        
        return new_portfolio
        
        
if __name__ == "__main__":
    policy = Policy(name="test", parameters={})
    
    policy.get_portfolio()