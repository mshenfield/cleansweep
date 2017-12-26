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
import logging
from threading import Thread

from cleansweep.constants import (
    ETHERDELTA_SOCKET_API_HOST,
    GET_MARKET,
)
from cleansweep.namespace import EtherDeltaNamespace
from cleansweep.ws_socket_io import WebSocketSocketIO

def _start_markets_thread(socket_io, period=30):
    """Emit a `GET_MARKET` event every `period` seconds"""
    def emit_markets():
        while True:
            socket_io.emit(GET_MARKET)
            time.sleep(period)

    markets_thread = Thread(target=emit_markets)
    markets_thread.start()
    return markets_thread

def run_client():
    """Periodically request `getMarket` and print any sweepable orders"""
    socket_io = WebSocketSocketIO(
        host=ETHERDELTA_SOCKET_API_HOST,
        Namepace=EtherDeltaNamespace,
    )
    markets_thread = start_markets_thread(socket_io)
    try:
        socket_io.wait()
    finally:
        # Wait for thread to exit because socket_io is borked
        markets_thread.join()
