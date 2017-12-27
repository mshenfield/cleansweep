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
from decimal import Decimal
import pprint

from cleansweep.constants import (
    logger,
    ETHERDELTA_REQUESTS_PER_MINUTE
)
from cleansweep.clients.etherdelta import EtherDeltaClient
from cleansweep.records import (
    EthOrder,
    Sweep,
    TokenSnapshot,
)

def print_maximum_sweep(token, sweeps):
    if not sweeps:
        logger.debug('No sweeps for candidate token {}'.format(token.ticker))
        return

    max_sweep = max(sweeps, key=lambda s: s.revenue)

    pprint.pprint({
        'ticker': token.ticker,
        'address': token.address,
        'revenue': max_sweep.revenue,
        'num_tokens': max_sweep.amount_of_tokens_to_buy,
        'buy_price': max_sweep.buy.price,
        'sell_price': max_sweep.sell.price,
    })

async def check_for_sweeps():
    async with EtherDeltaClient.connect() as socket:
        market = await socket.get_market()
        sweepable_tokens = [
            token for token in TokenSnapshot.from_market(market)
            if token.is_sweep_possible
        ]

        logger.info('Sweepable tokens: {}'.format(
            [(s.ticker, s.buy_to_sell_ratio) for s in sweepable_tokens]
        ))

        sweeps_by_token = {}
        for token in sweepable_tokens:
            api_orders = await socket.get_orders_for_token(token_address=token.address)
            sweeps = Sweep.sweeps_from_orders(api_orders)
            print_maximum_sweep(token, sweeps)
