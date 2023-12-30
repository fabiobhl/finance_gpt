# standard libraries
from enum import Enum
from dataclasses import dataclass, field
# third party imports
from alpaca.trading.enums import PositionSide as AlpacaPositionSide, OrderSide as AlpacaOrderSide
from alpaca.trading.models import Position as AlpacaPosition

class Symbol(Enum):
    ADBE = "Adobe"
    ADP = "Automatic Data Processing"
    ABNB = "Airbnb"
    GOOGL = "Alphabet Inc. (Class A)"
    GOOG = "Alphabet Inc. (Class C)"
    AMZN = "Amazon"
    AMD = "Advanced Micro Devices"
    AEP = "American Electric Power"
    AMGN = "Amgen"
    ADI = "Analog Devices"
    ANSS = "ANSYS"
    AAPL = "Apple"
    AMAT = "Applied Materials"
    ASML = "ASML Holding"
    AZN = "AstraZeneca"
    TEAM = "Atlassian"
    ADSK = "Autodesk"
    BKR = "Baker Hughes"
    BIIB = "Biogen"
    BKNG = "Booking Holdings"
    AVGO = "Broadcom"
    CDNS = "Cadence Design Systems"
    CDW = "CDW Corporation"
    CHTR = "Charter Communications"
    CTAS = "Cintas"
    CSCO = "Cisco Systems"
    CCEP = "Coca-Cola European Partners"
    CTSH = "Cognizant Technology Solutions"
    CMCSA = "Comcast"
    CEG = "Centogene"
    CPRT = "Copart"
    CSGP = "CoStar Group"
    COST = "Costco Wholesale"
    CRWD = "CrowdStrike"
    CSX = "CSX Corporation"
    DDOG = "Datadog"
    DXCM = "Dexcom"
    FANG = "Diamondback Energy"
    DLTR = "Dollar Tree"
    DASH = "DoorDash"
    EA = "Electronic Arts"
    EXC = "Exelon"
    FAST = "Fastenal"
    FTNT = "Fortinet"
    GEHC = "General Electric Healthcare"
    GILD = "Gilead Sciences"
    GFS = "G4S"
    HON = "Honeywell"
    IDXX = "IDEXX Laboratories"
    ILMN = "Illumina"
    INTC = "Intel"
    INTU = "Intuit"
    ISRG = "Intuitive Surgical"
    KDP = "Keurig Dr Pepper"
    KLAC = "KLA Corporation"
    KHC = "Kraft Heinz"
    LRCX = "Lam Research"
    LULU = "Lululemon Athletica"
    MAR = "Marriott International"
    MRVL = "Marvell Technology"
    MELI = "MercadoLibre"
    META = "Meta Platforms"
    MCHP = "Microchip Technology"
    MU = "Micron Technology"
    MSFT = "Microsoft"
    MRNA = "Moderna"
    MDLZ = "Mondelez International"
    MDB = "MongoDB"
    MNST = "Monster Beverage"
    NFLX = "Netflix"
    NVDA = "NVIDIA"
    NXPI = "NXP Semiconductors"
    ORLY = "O'Reilly Automotive"
    ODFL = "Old Dominion Freight Line"
    ON = "ON Semiconductor"
    PCAR = "PACCAR"
    PANW = "Palo Alto Networks"
    PAYX = "Paychex"
    PYPL = "PayPal"
    PDD = "Pinduoduo"
    PEP = "PepsiCo"
    QCOM = "Qualcomm"
    REGN = "Regeneron Pharmaceuticals"
    ROP = "Roper Technologies"
    ROST = "Ross Stores"
    SIRI = "Sirius XM Holdings"
    SPLK = "Splunk"
    SBUX = "Starbucks"
    SNPS = "Synopsys"
    TTWO = "Take-Two Interactive"
    TMUS = "T-Mobile US"
    TSLA = "Tesla"
    TXN = "Texas Instruments"
    TTD = "The Trade Desk"
    VRSK = "Verisk Analytics"
    VRTX = "Vertex Pharmaceuticals"
    WBA = "Walgreens Boots Alliance"
    WBD = "Woodward"
    WDAY = "Workday"
    XEL = "Xcel Energy"
    ZS = "Zscaler"
    
    @classmethod
    def from_string(cls, string: str):
        for symbol in cls:
            if symbol.name == string:
                return symbol
        raise ValueError(f"Unknown symbol {string}.")

class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"
    
    @classmethod
    def from_alpaca_side(cls, position_side: AlpacaPositionSide):
        if position_side == AlpacaPositionSide.LONG:
            return cls.LONG
        elif position_side == AlpacaPositionSide.SHORT:
            return cls.SHORT
        else:
            raise ValueError(f"Unknown side {position_side}.")

    def to_alpaca_order_side(self):
        if self == PositionSide.LONG:
            return AlpacaOrderSide.BUY
        elif self == PositionSide.SHORT:
            return AlpacaOrderSide.SELL
        else:
            raise ValueError(f"Unknown side {self}.")
    
@dataclass
class Position:
    symbol: Symbol
    amount: float
    side: PositionSide
    
    @classmethod
    def from_alpaca_position(cls, position: AlpacaPosition):
        return cls(
            amount=abs(float(position.qty)),
            side=PositionSide.from_alpaca_side(position.side),
            symbol=Symbol.from_string(position.symbol)
        )


@dataclass
class Portfolio():
    positions: list[Position] = field(default_factory=list)
    
    def add(self, position: Position) -> None:
        """Adds a position to the portfolio."""
        # check if the position is already in the portfolio
        for pos in self.positions:
            if pos.symbol == position.symbol:
                raise ValueError(f"Position for symbol {position.symbol} already exists.")
        
        # add a position to the portfolio
        self.positions.append(position)
        
        # sort the positions by symbol
        self.positions.sort(key=lambda x: x.symbol.name)
    
    def remove(self, position: Position) -> None:
        """Removes a position from the portfolio."""
        # check if the position is in the portfolio
        if not self.in_portfolio(position):
            raise ValueError(f"Position for symbol {position.symbol} does not exist.")
        
        # remove the position from the portfolio
        self.positions.remove(position)
    
    def reset(self) -> None:
        """Resets the portfolio."""
        self.positions = []
    
    def __post_init__(self) -> None:        
        # sort the positions by symbol
        self.positions.sort(key=lambda x: x.symbol.name)
        
        # make sure that the portfolio has no duplicate positions
        symbols = [pos.symbol for pos in self.positions]
        if len(symbols) != len(set(symbols)):
            raise ValueError("Portfolio contains duplicate positions.")
    
    def in_portfolio(self, position: Position) -> bool:
        """Checks if the given position is in the portfolio."""
        for pos in self.positions:
            if pos.symbol == position.symbol and pos.side == position.side:
                return True
        return False