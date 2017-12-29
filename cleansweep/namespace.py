"""Handlers for EtherDelta socket.io API"""

from ratelimiter import RateLimiter
from socketIO_client_nexus import BaseNamespace

from cleansweep.constants import (
    logger,
    ETHERDELTA_REQUESTS_PER_MINUTE,
    GET_MARKET,
    MARKET_ORDERS_KEY,
)


class EtherDeltaNamespace(BaseNamespace):
    def initialize(self):
        """Initialize an empty address to ticker mapping"""
        self.address_to_ticker = {}
        self.sweeps = set()

    #@RateLimiter(max_calls=ETHERDELTA_REQUESTS_PER_MINUTE, period=60)
    #def send(self, *args, **kwargs):
    #    """Rate limit sending a message to the EtherDelta API rate limit"""
    #    super(EtherDeltaNamespace, self).send(*args, **kwargs)

    def on_market_response(self, market):
        """Normally, get order details for sweepable `getMarket` tickers, otherwise print most profitable order"""
        if MARKET_ORDERS_KEY in market:
            return self._handle_market_orders(market[MARKET_ORDERS_KEY])

        sweepable_tokens = [
            token for token in TokenSnapshot.from_market(market)
            if token.is_sweep_possible
        ]

        logger.info('Sweepable tokens: {}'.format(
            [(s.ticker, s.address, s.buy_to_sell_ratio) for s in sweepable_tokens]
        ))

        for token in sweepable_tokens:
            self.address_to_ticker[token.address] = token.ticker
            # Request `GET_MARKET`
            self.emit(GET_MARKET, token_address=token.address)

        self.emit(GET_MARKET)

    def _handle_market_orders(self, orders):
        """Print the largest new sweep"""
        sweeps = Sweep.sweeps_from_orders(api_orders)
        new_sweeps = set(sweeps) - self.sweeps
        if not new_sweeps:
            logger.debug('No new sweeps in market orders response')

        max_sweep = max(new_sweeps, key=lambda s: s.revenue)
        new_sweeps.add(max_sweep)

        ticker = self.address_to_ticker[max_sweep.token_address]

        pprint.pprint({
            'address': token.address,
            'buy_price': max_sweep.buy.price,
            'num_tokens': max_sweep.amount_of_tokens_to_buy,
            'revenue': max_sweep.revenue,
            'risk_to_reward': max_sweep.risk_per_revenue,
            'sell_price': max_sweep.sell.price,
            'ticker': ticker,
        })
