"""Constants (like the EtherDelta URI)"""
from decimal import Decimal
import logging

logger = logging.getLogger('cleansweep')
logger.addHandler(logging.StreamHandler())

# Cost in Ether
BUY_GAS_ESTIMATE = 4843863
SELL_GAS_ESTIMATE = 2885709
GAS_PRICE = Decimal('.0000000051')
SWEEP_TXN_FEE_ETHER = (BUY_GAS_ESTIMATE + SELL_GAS_ESTIMATE) * GAS_PRICE

ETHER_TOKEN_ADDRESS = '0x0000000000000000000000000000000000000000'

# From https://www.reddit.com/r/EtherDelta/comments/6hrvwl/how_fees_work/
# .3% of the ETH in the sale goes to EtherDelta
ETHERDELTA_FEE_PROPORTION = Decimal('.003')
# Pick a particular server - otherwise we'll lose the session id
ETHERDELTA_SOCKET_API_URI = 'https://socket03.etherdelta.com'
# From https://github.com/etherdelta/etherdelta.github.io/blob/master/docs/API.md#user-content-rate-limit
# This is intentionally lower than the listed limit to avoid getting blocked
ETHERDELTA_REQUESTS_PER_MINUTE = 12

GET_MARKET = 'getMarket'

# string of the 'getMarket' event response
MARKET_EVENT_NAME = 'market'
MARKET_ORDERS_BUY_KEY = 'buys'
MARKET_ORDERS_KEY = 'orders'
MARKET_ORDERS_SELL_KEY = 'sells'
MARKET_ORDERS_TOKEN_GET_KEY = 'tokenGet'
MARKET_TICKERS_KEY = 'returnTickers'

# My maximum desired exposure (risk) in ETHER (~$400)
MAX_EXPOSURE_ETHER = Decimal('.5')
