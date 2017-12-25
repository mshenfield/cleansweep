"""Constants (like the EtherDelta URI)"""
from decimal import Decimal

ETHERDELTA_WS_URI = "wss://socket.etherdelta.com/socket.io/?transport=websocket"
MARKET_EVENT_NAME = "market"
# Based on previous transactions, we can estimate each trade is .0004 ether
ESTIMATED_TRADE_TXN_FEE_ETHER = Decimal('.0004')
# My maximum desired exposure (risk) in ETHER (~$400)
MAX_EXPOSURE_ETHER = Decimal('.5')
