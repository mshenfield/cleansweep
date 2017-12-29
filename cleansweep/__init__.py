"""
    `cleansweep` "cleans up" extant trades on EtherDelta by trying to complete
    buy/sell pairs where the buy (bid) is higher than sell (offer). Because
    EtherDelta isn't very automated, this situation appears regularly.

    `cleansweep` will always try to make a profitable trade, taking into account
    an estimation of cost for both trades based on the
        * GAS price
        * takers fee
        * profit (difference in buy/sell)
"""
import time

from socketIO_client_nexus import SocketIO

from cleansweep.constants import (
    ETHERDELTA_SOCKET_API_URI,
    GET_MARKET,
)
from cleansweep.namespace import EtherDeltaNamespace


def run_client():
    """Periodically request `getMarket` and print any sweepable orders"""
    with SocketIO(
        host=ETHERDELTA_SOCKET_API_URI,
        transports=['websocket'],
        Namespace=EtherDeltaNamespace,
    ) as io:
        io.emit(GET_MARKET)
        io.wait()
