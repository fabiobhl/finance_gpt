import datetime
import time
import pytz
import pandas_market_calendars as mcal

from finance_gpt import setup_logger

logger = setup_logger(__name__)

class Scheduler():
    
    def __init__(self) -> None:
        logger.debug("Initializing Scheduler.")
    
    def _check_market_open(self) -> tuple[bool, datetime.datetime, datetime.datetime]:
        """Checks if the market is opens today."""
        try:
            nasdaq = mcal.get_calendar('NASDAQ')
            date_to_check = datetime.datetime.now().date()
            schedule = nasdaq.schedule(start_date=date_to_check, end_date=date_to_check)

            if not schedule.empty:            
                return True, schedule.iloc[0]['market_open'].to_pydatetime(), schedule.iloc[0]['market_close'].to_pydatetime()
            else:
                return False, None, None
        except Exception as e:
            logger.exception("Error while checking if market is open.")
            return False, None, None
    
    def sleep(self, minutes: int = 10):
        """Sleeps until market opens again AM."""
        
        while True:
            # sleep until 12:00 AM
            self._sleep12()
            
            # check if market opens today
            market_opens, market_open_time, market_close_time = self._check_market_open()
            
            if market_opens:
                now = datetime.datetime.now()
                tz = pytz.timezone(str(market_open_time.tzinfo))
                time_dt = abs((market_open_time - tz.localize(now)).total_seconds()) - minutes * 60
                time.sleep(time_dt)
                return
        
    def _sleep12(self):
        """Sleeps until 12:00 AM."""
        try:
            # get current time
            now = datetime.datetime.now()
            
            if now.hour >= 12:
                next_date = datetime.datetime(now.year, now.month, now.day, 12, 0, 0) + datetime.timedelta(days=1)
            else:
                next_date = datetime.datetime(now.year, now.month, now.day, 12, 0, 0)
            
            # get time until 12:00 AM
            time_dt = abs((next_date - now).total_seconds())
            
            # sleep until 12:00 AM
            time.sleep(time_dt)
        except Exception as e:
            logger.exception("Error while sleeping until 12:00 AM, not sleeping.")
        
    def sleep_until_market_open(self):
        """Sleeps until market opens"""
            
        # check if market opens today
        market_opens, market_open_time, market_close_time = self._check_market_open()
        
        if market_opens:
            now = datetime.datetime.now()
            tz = pytz.timezone(str(market_open_time.tzinfo))
            time_dt = abs((market_open_time - tz.localize(now)).total_seconds())
            time.sleep(time_dt)
            return
        else:
            raise Exception("Market is closed today.")


class SentimentScheduler():
    
    def __init__(self, interval: int) -> None:
        self.interval = interval
        self.last_startup = None
        
    def sleep(self):
        """Sleep until next interval is reached"""       
        
        now = datetime.datetime.now()
        minute = now.minute
        
        before_minute = minute + (self.interval - minute % self.interval) - self.interval
        before_startup = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=before_minute)
        next_startup = before_startup + datetime.timedelta(minutes=self.interval)
        
        # make sure that sentimenting didnt take too long
        if self.last_startup is None:
            self.last_startup = datetime.datetime.now()
        if (next_startup - self.last_startup).total_seconds()/60 > self.interval:
            logger.error(f"Sentimenting took to long, last startup was: {self.last_startup}, next startup is: {next_startup}")
        self.last_startup = next_startup
        
        delta = (next_startup - datetime.datetime.now()).total_seconds()
        
        time.sleep(delta)
        
        
if __name__ == "__main__":
    sscheduler = SentimentScheduler(interval=5)
    
    sscheduler.sleep()