"""Client to etherdelta.com socket API"""
from decimal import Decimal

import websockets

from cleansweep.clients.socketio import SocketIOClient
from cleansweep.constants import (
    ETHERDELTA_WS_URI,
    MARKET_EVENT_NAME,
)


class EtherDeltaClient(SocketIOClient):
    """Client to etherdelta.com socket API"""
    URI = ETHERDELTA_WS_URI

    @classmethod
    def connect(cls, **kwargs):
        """Equivalent to `websockets.connect`, with `uri` and client preconfigured for EtherDelta"""
        if 'create_protocol' in kwargs:
            raise ValueError('`create_protocol` is preset to {}'.format(cls))

        return websockets.connect(cls.URI, create_protocol=cls, **kwargs)

    async def get_market(self, token_address=None, user_address=None):
        """Retreive the data result of the `getMarket` socket API endpoint."""
        kwargs = {}
        if token_address is not None:
            kwargs['token'] = token_address
        if user_address is not None:
            kwargs['user_address'] = user_address

        await self.send('getMarket', **kwargs)

        while True:
            event, market = await self.recv(json_loads_kwargs={'parse_float': Decimal})
            if event != MARKET_EVENT_NAME:
                continue
            return market
