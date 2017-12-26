"""Constants (like the EtherDelta URI)"""
from decimal import Decimal
import logging

logger = logging.getLogger('cleansweep')
logger.addHandler(logging.StreamHandler())

# Based on previous transactions, we can estimate each trade is .0004 ether
ESTIMATED_TRADE_TXN_FEE_ETHER = Decimal('.0004')

ETHER_TOKEN_ADDRESS = '0x0000000000000000000000000000000000000000'

ETHERDELTA_WS_URI = 'wss://socket.etherdelta.com/socket.io/?transport=websocket'
# From https://github.com/etherdelta/etherdelta.github.io/blob/master/docs/API.md#user-content-rate-limit
# This is intentionally lower than the listed limit to avoid getting blocked
ETHERDELTA_REQUESTS_PER_MINUTE = 10

# string of the 'getMarket' event response
MARKET_EVENT_NAME = 'market'
MARKET_ORDERS_BUY_KEY = 'buys'
MARKET_ORDERS_KEY = 'orders'
MARKET_ORDERS_SELL_KEY = 'sells'
MARKET_ORDERS_TOKEN_GET_KEY = 'tokenGet'
MARKET_TICKERS_KEY = 'returnTickers'

# My maximum desired exposure (risk) in ETHER (~$400)
MAX_EXPOSURE_ETHER = Decimal('.5')
