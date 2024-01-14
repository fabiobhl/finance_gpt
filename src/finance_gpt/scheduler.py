import datetime
import time
import pytz
import pandas_market_calendars as mcal

class Scheduler():
    
    def __init__(self) -> None:
        pass
    
    def _check_market_open(self) -> tuple[bool, datetime.datetime, datetime.datetime]:
        """Checks if the market is opens today."""
        
        nasdaq = mcal.get_calendar('NASDAQ')
        date_to_check = datetime.datetime.now().date()
        schedule = nasdaq.schedule(start_date=date_to_check, end_date=date_to_check)

        if not schedule.empty:            
            return True, schedule.iloc[0]['market_open'].to_pydatetime(), schedule.iloc[0]['market_close'].to_pydatetime()
        else:
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
        
    def sleep_until_market_open(self):
        """Sleeps until market opens"""
            
        # check if market opens today
        market_opens, market_open_time, market_close_time = self._check_market_open()
        
        if market_opens:
            now = datetime.datetime.now()
            time_dt = abs((market_open_time - pytz.timezone("Europe/Zurich").localize(now)).total_seconds())
            time.sleep(time_dt)
            return
        else:
            raise Exception("Market is closed today.")
    
      
if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.sleep()