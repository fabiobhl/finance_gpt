from finance_gpt import setup_logger
from finance_gpt.scheduler import Scheduler
from finance_gpt.portfolio_manager import PortfolioManager
from finance_gpt.policy import Policy

logger = setup_logger("policy_runner")

AMOUNT_OF_STOCKS = 15

if __name__ == "__main__":
    
    # setup
    logger.debug("Starting Finance GPT.")
    logger.debug("Setting up Scheduler, and PortfolioManager.")
    try:
        # timer
        scheduler = Scheduler()
        # portfolio manager
        pm = PortfolioManager()
        # setup policy
        policy = Policy(name="normal", parameters={})
    except Exception as e:
        logger.exception("t")
        exit()
    
    # main loop
    try:
        while True:
            logger.debug(50*"=" + "Starting new loop." + 50*"=")
            
            # sleep until market opens (5 minutes before)
            minutes_before = 5
            logger.debug(f"Sleeping until {minutes_before} minutes before market opens.")
            scheduler.sleep(minutes=minutes_before)
            
            # run policy
            new_portfolio = policy.get_portfolio()
            
            # wait for markets to open
            logger.debug("Waiting for markets to open.")
            scheduler.sleep_until_market_open()
            logger.debug("Markets opened.")
            
            # update the portfolio accordingly
            logger.debug("Updating the portfolio accordingly online")
            pm.update(new_portfolio=new_portfolio)
            logger.debug("Portfolio updated.")
        
    except:
        logger.exception("Failed in main loop")
        