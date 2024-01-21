from finance_gpt import setup_logger
from finance_gpt.scheduler import Scheduler
from finance_gpt.news_api import load_all_news
from finance_gpt.gpt import GPT
from finance_gpt.portfolio_manager import PortfolioManager
import pandas as pd

logger = setup_logger(__name__)

AMOUNT_OF_STOCKS = 15

if __name__ == "__main__":
    
    # setup
    logger.debug("Starting Finance GPT.")
    logger.debug("Setting up Scheduler, GPT and PortfolioManager.")
    try:
        # timer
        scheduler = Scheduler()
        # sentiment model
        gpt = GPT()
        # portfolio manager
        pm = PortfolioManager()
    except Exception as e:
        logger.exception("t")
        exit()
    
    # main loop
    while True:
        logger.debug(50*"=" + "Starting new loop." + 50*"=")
        
        # sleep until market opens (15 minutes before)
        minutes_before = 30
        logger.debug(f"Sleeping until {minutes_before} minutes before market opens.")
        try:
            scheduler.sleep(minutes=minutes_before)
        except Exception as e:
            logger.exception("t")
            continue
        
        # load news
        logger.debug("Loading news.")
        try:
            news = load_all_news()
        except Exception as e:
            logger.exception("t")
            exit()
        
        # sentiment them with chat gpt
        logger.debug("Sentimenting news.")
        try:
            for key, value in news.items():
                for news_article in value:
                    gpt.get_sentiment(news_article, term="short")
        except Exception as e:
            logger.exception("t")
            exit()
        
        # calculate sentiment score
        logger.debug("Calculating sentiment score.")
        try:
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
        except Exception as e:
            logger.exception("t")
            exit()
        
        
        # get the best stocks (AMOUNT_OF_STOCKS)
        logger.debug(f"Getting the {AMOUNT_OF_STOCKS} best stocks.")
        try:
            score_df = pd.DataFrame.from_dict(scores, orient="index", columns=["score"])
            score_df["absolute_score"] = abs(score_df["score"])
            sorted_score_df = score_df.sort_values(by="absolute_score", ascending=False)
            new_stocks = sorted_score_df.iloc[:AMOUNT_OF_STOCKS, :]
        except Exception as e:
            logger.exception("t")
            exit()
        logger.debug(f"New stocks: {new_stocks}")
        
        # cut the scores to have a absolute value bigger than 0.7
        logger.debug("Cutting the scores to have a absolute value bigger than 0.7.")
        try:
            new_stocks = new_stocks[new_stocks["absolute_score"] >= 0.7]
        except Exception as e:
            logger.exception("t")
            exit()
        logger.debug(f"New stocks: {new_stocks}")
        
        # create the portfolio
        logger.debug("Creating the portfolio.")
        try:
            new_portfolio = pm.create_portfolio(new_stocks)
        except Exception as e:
            logger.exception("t")
            exit()
        logger.debug(f"New portfolio: {new_portfolio}")
        
        # wait for markets to open
        logger.debug("Waiting for markets to open.")
        try:
            scheduler.sleep_until_market_open()
        except Exception as e:
            logger.exception("t")
            exit()
        logger.debug("Markets opened.")
        
        # update the portfolio accordingly
        logger.debug("Updating the portfolio accordingly online")
        try:
            pm.update(new_portfolio=new_portfolio)
        except Exception as e:
            logger.exception("t")
            exit()
        logger.debug("Portfolio updated.")
        
        