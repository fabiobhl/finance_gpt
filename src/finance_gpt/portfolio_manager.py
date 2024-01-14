# standard libraries
import time
# finance_gpt imports
from finance_gpt import setup_logger
from finance_gpt.structures import Portfolio, Position, Symbol, PositionSide
from finance_gpt.utils import load_credentials
# third party imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest
import pandas as pd

logger = setup_logger(__name__)

class PortfolioManager():
    
    def __init__(self) -> None:
        # setup of alpaca api
        key, secret = self._load_credentials()
        self.trading_client = TradingClient(
            api_key=key,
            secret_key=secret,
        )
        self.account = self.trading_client.get_account()
        self.data_client = StockHistoricalDataClient(
            api_key=key,
            secret_key=secret,
        )
        
        # setup of portfolio
        self.portfolio = Portfolio()
        self._sync_portfolio()
        
    def update(self, new_portfolio: Portfolio) -> None:
        """Updates the portfolio according to the new portfolio."""
        # sync the portfolio
        self._sync_portfolio()
        
        # close all positions that are not in the new portfolio
        for old_position in self.portfolio.positions:
            if not new_portfolio.in_portfolio(old_position):
                self.trading_client.close_position(old_position.symbol.name)
                self.portfolio.remove(old_position)
                
        # wait for all orders to be filled
        self._wait_for_orders()
                
        # open all positions that are not in the old portfolio
        for new_position in new_portfolio.positions:
            if not self.portfolio.in_portfolio(new_position):
                market_order_data = MarketOrderRequest(
                    symbol=new_position.symbol.name,
                    qty=new_position.amount,
                    side=new_position.side.to_alpaca_order_side(),
                    time_in_force=TimeInForce.DAY
                )
                self.trading_client.submit_order(order_data=market_order_data)
    
    def _sync_portfolio(self) -> None:
        """Syncs the positions in the portfolio with the positions in the Alpaca API."""
        
        # reset the portfolio
        self.portfolio.reset()
        
        # get positions from Alpaca API
        alpaca_positions = self.trading_client.get_all_positions()
        
        # convert to positions and add to portfolio
        for alpaca_position in alpaca_positions:
            self.portfolio.add(Position.from_alpaca_position(alpaca_position))
        
    def _load_credentials(self) -> tuple[str, str]:
        """Loads the credentials from the credentials.json file."""
        # load the credentials
        creds = load_credentials()
        
        # extract keys
        try:
            key = creds["alpaca"]["paper"]["key"]
            secret = creds["alpaca"]["paper"]["secret"]
            return key, secret
        except Exception:
            print("credentials.json file does not contain alpaca credentials.")
            raise Exception
    
    def _wait_for_orders(self) -> None:
        """Waits for all orders to be filled."""
        
        # get all open orders
        order_request_filter = GetOrdersRequest(status=QueryOrderStatus.OPEN)
        open_orders = self.trading_client.get_orders(filter=order_request_filter)
        
        # wait for all open orders to be filled
        while len(open_orders) > 0:
            open_orders = self.trading_client.get_orders(filter=order_request_filter)
            time.sleep(10)
    
    def create_portfolio(self, stock_table: pd.DataFrame) -> Portfolio:
        """Creates a portfolio from a buy list."""
        logger.debug(f"Creating portfolio from stock table: {stock_table}")
        
        # instantiate new portfolio
        portfolio = Portfolio()
        
        # calculate buy power
        amount = float(self.account.portfolio_value) - 10
        # calculate the amount of stocks
        num_stocks = len(stock_table)
        
        # add the positions to the portfolio
        for index, row in stock_table.iterrows():
            # get the symbol
            symbol = Symbol.from_string(index)
            
            logger.debug(f"Adding position for symbol {symbol}.")
            logger.debug(f"Money available: {amount}, number of stocks: {num_stocks}.")
            
            # get side
            if row["score"] < 0:
                side = PositionSide.SHORT
            else:
                side = PositionSide.LONG
            logger.debug(f"Side: {side}")
            
            # get the amount of stocks
            stock_price = self._get_price(symbol)
            stock_amount = (amount / num_stocks) / stock_price
            logger.debug(f"Stock price: {stock_price}, stock amount: {stock_amount}")
            
            # if the side is short, round the amount of stocks (can only be integer)
            if side == PositionSide.SHORT:
                logger.debug("Shorting Stock -> need to have rounded stock amount.")
                
                # calculate the amount of stocks
                rounded_stock_amount = round(stock_amount)
                logger.debug(f"Rounded stock amount: {rounded_stock_amount}")
                
                if rounded_stock_amount == 0:
                    logger.debug("Rounded stock amount is 0, not adding position to new portfolio.")
                    continue
                
                # check if symbol is shortable
                if not self.trading_client.get_asset("AMZN").shortable:
                    logger.debug("Symbol is not shortable, not adding position to new portfolio.")
                    continue
                    
                stock_amount = rounded_stock_amount
    
            # add the position to the portfolio
            portfolio.add(Position(
                symbol=symbol,
                amount=stock_amount,
                side=side)
            )
            logger.debug(f"Added position for symbol {symbol} to new portfolio, amount: {stock_amount}, side: {side}.")
            
            # update the amount and number of stocks
            amount -= stock_amount * stock_price
            num_stocks -= 1
        
        return portfolio
    
    def _get_price(self, symbol: Symbol) -> float:
        """Gets the current price of a stock."""
        rq_params = StockLatestBarRequest(symbol_or_symbols=symbol.name)
        latest_bar = self.data_client.get_stock_latest_bar(request_params=rq_params)
        return latest_bar[symbol.name].close
     
if __name__ == "__main__":
    # test the portfolio manager
    pm = PortfolioManager()
    
    new_stocks = pd.DataFrame({"score": [-1, 0.2, 0.1, 0], "absolute_score": [1, 0.2, 0.1, 0]}, index=["ABNB", "GOOGL", "GOOG", "AMZN"])
    
    new_portfolio = pm.create_portfolio(new_stocks)
    
    pm.update(new_portfolio=new_portfolio)
    