import asyncio

from cleansweep.feed import loop

token_summaries = asyncio.get_event_loop().run_until_complete(loop())

ticker_ratios = ((t.ticker, t.bid_ask_ratio) for t in token_summaries)
print(sorted(
    ticker_ratios,
    # Highest ratio first
    key=lambda t: -t[1],
))

# Get book for each token
