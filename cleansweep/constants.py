"""Constants (like the EtherDelta URI)"""
from decimal import Decimal
import logging

logger = logging.getLogger('cleansweep')
logger.addHandler(logging.StreamHandler())

# Based on previous transactions. The sell is .0003825 the buy is .0003205 when buying at 4.1 gas price
# This is at 5.1, for almost nothing can get much faster confirmation
# Cost in Ether
BUY_GAS = 4843863
SELL_GAS = 2885709
GAS_PRICE = Decimal('.000000001')
SWEEP_TXN_FEE_ETHER = (BUY_GAS + SELL_GAS) * GAS_PRICE

# Max order book update time seen : 5 minutes

ETHER_TOKEN_ADDRESS = '0x0000000000000000000000000000000000000000'

# From https://www.reddit.com/r/EtherDelta/comments/6hrvwl/how_fees_work/
# .3% of the ETH in the sale goes to EtherDelta
ETHERDELTA_FEE_PROPORTION = Decimal('.003')
# From https://github.com/etherdelta/etherdelta.github.io/blob/master/docs/API.md#user-content-rate-limit
ETHERDELTA_REQUESTS_PER_MINUTE = 12
ETHERDELTA_WS_URI = 'wss://socket.etherdelta.com/socket.io/?transport=websocket'

# string of the 'getMarket' event response
MARKET_EVENT_NAME = 'market'
MARKET_ORDERS_BUY_KEY = 'buys'
MARKET_ORDERS_KEY = 'orders'
MARKET_ORDERS_SELL_KEY = 'sells'
MARKET_ORDERS_TOKEN_GET_KEY = 'tokenGet'
MARKET_TICKERS_KEY = 'returnTickers'

# My maximum desired exposure (risk) in ETHER (~$400)
MAX_EXPOSURE_ETHER = Decimal('.5')
