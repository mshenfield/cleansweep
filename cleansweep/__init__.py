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
import asyncio
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

seen_sweeps = set()

def print_maximum_sweep(token, sweeps):
    new_sweeps = set(sweeps) - seen_sweeps
    if not new_sweeps:
        logger.debug('No new sweeps for candidate token {}'.format(token.ticker))
        return

    max_sweep = max(new_sweeps, key=lambda s: s.revenue)

    seen_sweeps.add(max_sweep)

    pprint.pprint({
        'ticker': token.ticker,
        'address': token.address,
        'risk_to_reward': max_sweep.risk_per_revenue,
        'revenue': max_sweep.revenue,
        'num_tokens': max_sweep.amount_of_tokens_to_buy,
        'buy_price': max_sweep.buy.price,
        'sell_price': max_sweep.sell.price,
    })

async def check_for_sweeps():
    async with EtherDeltaClient.connect() as socket:
        while True:
            market = await socket.get_market()
            sweep_candidates = (
                token for token in TokenSnapshot.from_market(market)
                if token.is_sweep_possible
            )
            sweep_candidates = sorted(sweep_candidates, key=lambda t: -t.buy_to_sell_ratio)

            logger.info('Sweep candidates: {}'.format(
                [(s.ticker, s.address, s.buy_to_sell_ratio) for s in sweep_candidates]
            ))

            sweeps_by_token = {}
            for token in sweep_candidates:
                api_orders = await socket.get_orders_for_token(token_address=token.address)
                sweeps = Sweep.sweeps_from_orders(api_orders)
                print_maximum_sweep(token, sweeps)

            logger.info('Completed sweep, resting for 10 seconds')
            await asyncio.sleep(10)
