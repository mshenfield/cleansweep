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

def print_most_profitable_sweeps(sweeps_by_token):
    """Prints the most profitable sweep for each token in `sweeps_by_token`"""
    # Print from most profitable to least
    token_sweeps = []
    for token, sweeps in sweeps_by_token.items():
        max_sweep = max(sweeps, key=lambda s: s.revenue)
        token_sweeps.append({
            'ticker': token,
            'revenue': max_sweep.revenue,
            'num_tokens': max_sweep.amount_of_tokens_to_buy,
            'buy_price': max_sweep.buy.price,
            'sell_price': max_sweep.sell.price,
        })

    pprint.pprint(sorted(
        token_sweeps,
        # Revenue descending
        key=lambda s: -s['revenue'],
    ))

class Dispatcher:
    """Stores state and dispatches actions based on socket events"""
    def __init__(self):
        self.address_to_ticker = {}
        self.order_by_token = None

    async def __call__(self, event_name, message):
        handler = self._get_handler(event_name)
        if handler:
            return await handler(message)
        else:
            logger.debug('Unhandled event "{}"'.format(event_name))
            return

    def _get_handler(self, event_name):
        """Returns the handler function for `event_name` or None if there isn't one"""
        return getattr(self, self._handler_name(event_name), None)

    def _handler_name(self, event_name):
        """Returns the name of the handler for an event (case sensitive)"""
        return 'on_{}'.format(event_name)

    def _print_best_sweep(ticker, sweeps):
        """Print execution information on most profitable sweep"""
        max_sweep = max(sweeps, key=lambda s: s.revenue)
        print({
                'ticker': ticker,
                'revenue': max_sweep.revenue,
                'num_tokens': max_sweep.amount_of_tokens_to_buy,
                'buy_price': max_sweep.buy.price,
                'sell_price': max_sweep.sell.price,
        })

    async def on_market(self, market):
        if not market:
            logger.debug('Skipping empty market event response')
            return

        if MARKET_ORDERS_KEY in market:
            logger.debug('Received "orders" in market response')
            return self.on_market_orders(market[MARKET_ORDERS_KEY])
        else:
            tokens = TokenSnapshot.from_market(market)
            self.address_to_ticker.update({
                t.address: t.ticker
                for t in tokens
            })

            # Asynchronously check for new sweepable tokens
            self.sweepable_tokens = [
                t for t in tokens
                if t.is_sweep_possible
            ]

            logger.info('Sweepable tokens: {}'.format(
                [(s.ticker, s.buy_to_sell_ratio) for s in sweepable_tokens]
            ))

            for token in sweepable_tokens:
                # Request a `getMarket` with `token_address` populated, which
                # will return a MARKET_ORDERS_KEY for this token's orders. We
                # need to get detailed order information to check actual profitability.
                await socket.emit_get_market(token_address=token.address)

            await socket.emit_get_market()

    def on_market_orders(self, api_orders):
        """Handle when a `getMarket` response which includes an MARKET_ORDERS_KEY key

        This occurs when `token_address` is populated in the data.  We maintain
        a mapping of addresses to token tickers, because the actual ticker is
        not returned here, just the address.

        This just prints out the most profitable sweep right now.
        """
        sweeps = Sweep.sweeps_from_get_market_orders(api_orders)
        if not sweeps:
            logger.debug('No sweeps in market orders response')

        # The api_orders response doesn't include tickers, but is homogenous
        # and we need the ticker to manually look at results
        ticker = self.address_to_ticker.get(sweeps[0].token_address)
        if not ticker:
            raise ValueError(
                'No ticker entry for token address: {}'.format(token_address)
            )
        self._print_best_sweep(ticker, sweeps)

# def interval(callable, period):
#     """Call `callable` every `period` seconds, asynchronously"""
#     while True:
#         callable()
#         asyncio.sleep(period)
#
async def listen():
    """Starts a client that listens and reacts to events"""
    async with EtherDeltaClient.connect() as socket:
        # Request market every minute
        await socket.emit_get_market()

        dispatcher = Dispatcher()
        await socket.listen(handler=dispatcher)
