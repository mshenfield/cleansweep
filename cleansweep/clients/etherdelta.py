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

    async def get_market(self, token_address=None, user_address=None):
        """Call the `getMarket` API and return the response by polling the socket API"""
        kwargs = {}
        if token_address is not None:
            kwargs['token'] = token_address
        if user_address is not None:
            kwargs['user_address'] = user_address

        await self.send('getMarket', **kwargs)

        while True:
            event, market = await self.recv(json_loads_kwargs={'parse_float': Decimal})
            market_is_empty = not market
            if event != MARKET_EVENT_NAME:
                logger.debug('Skipping non-market event response "{}"'.format(event))
                continue

            # XXX: Periodically this seems to come back empty, we skip and try again
            if not market:
                logger.debug('Skipping empty market event response')
                continue

            return market

    async def get_orders_for_token(self, token_address):
        """Get open orders for the token at `token_addres`

        Returns the `MARKET_ORDERS_KEY` value of the `getMarket` API response.
        """
        market = {}
        while MARKET_ORDERS_KEY not in market:
            market = await self.get_market(token_address=token_address)

        token_orders = market[MARKET_ORDERS_KEY]
        sample_api_order = safe_choice(
            token_orders[MARKET_ORDERS_BUY_KEY] + token_orders[MARKET_ORDERS_SELL_KEY]
        )
        sample_order = sample_api_order and EthOrder.from_api_order(sample_api_order)
        token_mismatch = (
            sample_order and
            sample_order.token_address != token_address
        )
        if token_mismatch:
            raise ValueError(
                'Received response for different token. Expected {}, Actual {}'.format(
                    token_address,
                    sample_order.token_address,
                )
            )
        return token_orders

    async def get_token_summaries(self):
        """Retreive a mapping of tokens to a summary of order activity on EtherDelta.

        This returns the MARKET_TICKERS_KEY key from response of the `getMarket` socket API call.
        """
        market = await self.get_market()
        if MARKET_TICKERS_KEY not in market:
            raise ValueError('Got market with no ticker summaries: {}'.format(market))
        return market[MARKET_TICKERS_KEY]
