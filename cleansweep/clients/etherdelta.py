"""Client to etherdelta.com socket API"""
from decimal import Decimal
from random import choice

from ratelimiter import RateLimiter
import websockets

from cleansweep.clients.socketio import SocketIOClient
from cleansweep.constants import (
    logger,
    ETHERDELTA_REQUESTS_PER_MINUTE,
    ETHERDELTA_WS_URI,
    MARKET_EVENT_NAME,
    MARKET_ORDERS_BUY_KEY,
    MARKET_ORDERS_KEY,
    MARKET_ORDERS_SELL_KEY,
    MARKET_ORDERS_TOKEN_GET_KEY,
    MARKET_TICKERS_KEY,
)
from cleansweep.records import EthOrder

def safe_choice(seq):
    """Choose a random element from a sequence or None if the sequence is empty"""
    try:
        return choice(seq)
    except IndexError:
        return None


class EtherDeltaClient(SocketIOClient):
    """Client to etherdelta.com socket API"""
    URI = ETHERDELTA_WS_URI

    def __init__(self, *args, **kwargs):
        """Initialize `EtherDeltaClient` with a rate limited send to respect API limit"""
        super(EtherDeltaClient, self).__init__(*args, **kwargs)
        # Rate limit our `send` function to match ETHERDELTA requests
        rl = RateLimiter(max_calls=ETHERDELTA_REQUESTS_PER_MINUTE, period=60)
        self.send = rl(self.send)

    @classmethod
    def connect(cls, **kwargs):
        """Equivalent to `websockets.connect`, with `uri` and client preconfigured for EtherDelta"""
        if 'create_protocol' in kwargs:
            raise ValueError('`create_protocol` is preset to {}'.format(cls))

        return websockets.connect(cls.URI, create_protocol=cls, **kwargs)

    async def listen(self, handler):
        # self.keepalive()

        async for data in self:
            if data is None:
                continue
            else:
                event, message = data
                await handler(event, message)

    async def recv(self):
        """Harcode in parsing floats as Decimals for the EtherDelta client"""
        await super(EtherDeltaClient, self).recv(json_loads_kwargs={'parse_float': Decimal})

    async def emit_get_market(self, token_address=None, user_address=None):
        """Emit a `getMarket` call to the API"""
        kwargs = {}
        if token_address is not None:
            kwargs['token'] = token_address
        if user_address is not None:
            kwargs['user_address'] = user_address

        await self.send('getMarket', **kwargs)
