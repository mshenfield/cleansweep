"""Record classes for the EtherDelta tokens API"""
import decimal

import attr


def none_or_decimal(value):
    """Return None if value is None, else create a Decimal from the value"""
    if value is None:
        return None
    return decimal.Decimal(value)

@attr.s
class TokenSummary:
    """Summary information about a particular token on EtherDelta (e.g. ETH)"""
    # Ticker symbol of token
    ticker = attr.ib()
    # The address of the token's contract
    token_address = attr.ib()
    # ?
    quote_volume = attr.ib()
    # ?
    base_volume = attr.ib()
    # Price of the last trade
    last_trade = attr.ib()
    # Percent change of the last trade from the trade before
    percent_change = attr.ib()
    # Largest price of extant buy order
    bid = attr.ib()
    # Lowest price of extant sell order
    ask = attr.ib()

    @property
    def sweep_is_possible(self):
        """Returns True if it is possible for a sweep to be profitable on this token

        It's possibly profitable if the largest buy is higher than the lowest sell.
        The actual profitability depends on estimated transaction fees, and quantity
        of tokens that can be transacted, which is why it is calculated separately.
        """
        return self.bid_ask_ratio > decimal.Decimal('1')

    @property
    def bid_ask_ratio(self):
        """Ratio of the highest sell price to the lowest sales prices

        If this is higher than one, it means that a bid executed quickly enough can reap
        profit.
        """
        # Sometimes there is no buy or sells. Just throwing something against the wall, ratio of 0 seems safe
        if self.ask is None or self.bid is None:
            return decimal.Decimal('0')

        try:
            return self.bid / self.ask
        except decimal.DivisionByZero:
            # If bid is zero, infinity is a mathematically correct and useful answer
            # It gives a correct indication that the ratio is high
            return decimal.Decimal('Infinity')
        except decimal.InvalidOperation:
            # This occurs when 0 / 0, but could also occur elsewhere. Return 0 to be safe
            return decimal.Decimal('0')

    @classmethod
    def from_market(cls, market):
        """Return a list of TokenSummary from a `market` object with `returnTicker` populated"""
        if 'returnTicker' not in market:
            raise ValueError("'returnTicker' not found in `market`: {}".format(market))

        # Use dict for numeric values
        return [
            cls(
                ticker=ticker,
                token_address=token_summary['tokenAddr'],
                quote_volume=token_summary['quoteVolume'],
                base_volume=token_summary['baseVolume'],
                # lastTrade is None if there is no last trade
                last_trade=none_or_decimal(token_summary['last']),
                # percentChange is None when it is the first posting for that ticker
                percent_change=none_or_decimal(token_summary['percentChange']),
                # bid is None when are no bids
                bid=none_or_decimal(token_summary['bid']),
                # ask is None when there is no ask
                ask=none_or_decimal(token_summary['ask']),
            )
            for ticker, token_summary in market['returnTicker'].items()
        ]
