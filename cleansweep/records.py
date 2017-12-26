"""Record classes for the EtherDelta tokens API"""
import decimal
import enum
from itertools import (
    product,
    takewhile,
)

import attr

from cleansweep.constants import (
    ESTIMATED_TRADE_TXN_FEE_ETHER,
    ETHER_TOKEN_ADDRESS,
    MARKET_ORDERS_BUY_KEY,
    MARKET_ORDERS_SELL_KEY,
    MAX_EXPOSURE_ETHER,
)

def none_or_decimal(value):
    """Return None if value is None, else create a Decimal from the value"""
    if value is None:
        return None
    return decimal.Decimal(value)

@attr.s
class TokenSnapshot:
    """Summary information about a particular token on EtherDelta (e.g. ETH)"""
    # Ticker symbol of token, e.g. ETH
    ticker = attr.ib()
    # The address of the token's contract
    address = attr.ib()
    # Current highest price of an extant buy order
    buy = attr.ib()
    # Lowest price of extant sell order
    sell = attr.ib()

    @property
    def is_sweep_possible(self):
        """Returns True if it is possible for a sweep to be profitable on this token

        It's possibly profitable if the largest buy is higher than the lowest sell.
        The actual profitability depends on estimated transaction fees, and quantity
        of tokens that can be transacted, which is why it is calculated separately.
        """
        return self.buy_to_sell_ratio > decimal.Decimal('1')

    @property
    def buy_to_sell_ratio(self):
        """Ratio of the highest sell price to the lowest sales prices

        If this is higher than one, it means that a bid executed quickly enough can reap
        profit.
        """
        # Sometimes there is no buy or sells. Just throwing something against the wall, ratio of 0 seems safe
        if self.buy is None or self.sell is None:
            return decimal.Decimal('0')

        try:
            return self.buy / self.sell
        except decimal.DivisionByZero:
            # If bid is zero, infinity is a mathematically correct and useful answer
            # It gives a correct indication that the ratio is high
            return decimal.Decimal('Infinity')
        except decimal.InvalidOperation:
            # This occurs when 0 / 0, but could also occur elsewhere. Return 0 to be safe
            return decimal.Decimal('0')

    @classmethod
    def from_market(cls, market):
        """Return a list of TokenSnapshot from a `market` dict"""
        if 'returnTicker' not in market:
            raise ValueError("'returnTicker' not found in `market`: {}".format(market))

        # Use dict for numeric values
        return [
            cls(
                ticker=ticker,
                address=token_snapshot['tokenAddr'],
                # None if are no buy orders
                buy=none_or_decimal(token_snapshot['bid']),
                # None if are no sell orders
                sell=none_or_decimal(token_snapshot['ask']),
            )
            for ticker, token_snapshot in market['returnTicker'].items()
        ]


class OrderType(enum.Enum):
    BUY = enum.auto()
    SELL = enum.auto()
    UNKNOWN = enum.auto()

@attr.s
class EthOrder:
    """Represents an order in the "Order Book" trading an ERC-20 token for ETH"""
    # Amount of non-ETH token being offered or asked for
    token_amount = attr.ib()
    # Amount of ETH being offered or asked for
    eth_amount = attr.ib()
    # Price in ETH
    price = attr.ib()
    # Last time this Order was updated
    updated = attr.ib()
    # Token being asked for
    token_get_address = attr.ib()
    # Token being provided
    token_give_address = attr.ib()

    @token_get_address.validator
    def one_token_is_eth(self, *args, **kwargs):
        """Exactly one of the giving or receiving token is ETH"""
        # `^` is the xor operator - one but not both
        return (
            (self.token_get_address == ETHER_TOKEN_ADDRESS) ^
            (self.token_give_address == ETHER_TOKEN_ADDRESS)
        )

    @property
    def token_address(self):
        """Address of the non-ETH token in the trade"""
        if self.order_type == OrderType.SELL:
            return self.token_give_address
        else:
            return self.token_get_address

    @property
    def order_type(self):
        """The OrderType of the order"""
        # If you're expecting ETH, then you're selling
        if self.token_get_address == ETHER_TOKEN_ADDRESS:
            return OrderType.SELL
        else:
            # and otherwise you're expecting to give ETH, and you're buying
            return OrderType.BUY

    @classmethod
    def from_api_order(cls, api_order):
        """Create an EthOrder from an order returned by the EtherDelta API"""
        return cls(
            token_amount=decimal.Decimal(api_order['ethAvailableVolume']),
            eth_amount=decimal.Decimal(api_order['ethAvailableVolumeBase']),
            price=decimal.Decimal(api_order['price']),
            updated=api_order['updated'],
            token_get_address=api_order['tokenGet'],
            token_give_address=api_order['tokenGive'],
        )

    @classmethod
    def from_get_market_orders(cls, orders):
        """Return a list of buys and sells from a `getMarket` order buys and sells"""
        # Note for all of these - I don't make the names, I just interpret the tea leaves
        buys = [cls.from_api_order(ai) for ai in orders[MARKET_ORDERS_BUY_KEY]]
        sells = [cls.from_api_order(ai) for ai in orders[MARKET_ORDERS_SELL_KEY]]
        return buys, sells


@attr.s
class Sweep:
    """A pair of open buy/sell orders that we instantly trade to try and make a profit.

    The main method here is `is_profitable`, which tells if a sweep would be profitable.
    You can also read the raw amount from `revenue`.

    """
    buy = attr.ib()
    sell = attr.ib()

    @buy.validator
    def _validate_order_tokens_match(self, *args, **kwargs):
        """Can only buy and sell like tokens"""
        return self.buy.token_address == self.sell.token_address

    @classmethod
    def sweeps_from_orders(cls, orders):
        """Returns a list of profitable `Sweep` objects from the `getMarket` orders API response

        Params:
            `orders` - MARKET_ORDERS_KEY from the `getMarket` orders response. This has a
            dictionary with two entries: a list of buys and a list of sells
        Notes:
            To avoid comparing every buy to every sell, this only pairs buys
            that are offering more than the lowest sell price, and sells before
            the first sell above the highest buy price. If there are no buys/sells,
            no pairs are generated.
        """
        buys, sells = EthOrder.from_get_market_orders(orders)
        # No pairings if there isn't anything to match
        if not buys and not sells:
            return []

        # Sells are ordered from lowest ask to highest
        lowest_sell = sells[0]

        def is_sell_below_highest_buy(sell):
            """True if sell.price is below the highest buy's price (e.g. could be sold for profit)"""
            # Buys are ordered from highest offer to lowest
            highest_buy = buys[0]
            return sell.price < highest_buy.price

        sweepable_buys = (b for b in buys if b.price > lowest_sell.price)
        sweepable_sells = takewhile(is_sell_below_highest_buy, sells)
        possible_sweeps = (
            cls(b, s) for (b, s) in
            product(sweepable_buys, sweepable_sells)
        )
        return [s for s in possible_sweeps if s.is_profitable]


    @property
    def estimated_fees(self):
        """The estimated transaction fees"""
        # Pay txn fee for both purchasing and selling
        return ESTIMATED_TRADE_TXN_FEE_ETHER * 2

    @property
    def available_tokens(self):
        """The total amount of tokens available to instantly buy/sell"""
        return min(self.buy.token_amount, self.sell.token_amount)

    @property
    def amount_of_tokens_to_buy(self):
        """Return the amount of tokens we're able/willing to to purchase

        This returns the maximum number of tokens purchasable for up to the price of
        `constants.MAX_EXPOSURE_ETHER`.
        """
        eth_for_all_available = self.available_tokens * self.sell.price
        # Only spend up to `MAX_EXPOSURE_ETHER`
        eth_spend = min(MAX_EXPOSURE_ETHER, eth_for_all_available)
        # If `eth_spend` is `eth_for_all_available`, we buy all available, otherwise
        # only buy up to our limit.
        return (eth_spend / eth_for_all_available) * self.available_tokens

    @property
    def price_difference(self):
        """Difference between the buy and sell price"""
        return self.buy.price - self.sell.price

    @property
    def revenue(self):
        """The amount of revenue (negative or positive) that would be generated by executing this sweep"""
        return self.amount_of_tokens_to_buy * self.price_difference - self.estimated_fees

    @property
    def is_profitable(self):
        """Returns True if the `buy`/`sell` pair can be swept for a profit"""
        return self.revenue > decimal.Decimal('0')
