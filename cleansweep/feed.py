"""The `start` method sets up a loop that queries the EtherDelta API and prints (for now) profitable trades"""
from decimal import Decimal

from cleansweep.clients.etherdelta import EtherDeltaClient
from cleansweep.records import TokenSummary

async def loop():
    async with EtherDeltaClient.connect() as socket:
        market = await socket.get_market()
        return [
            summary for summary in TokenSummary.from_market(market)
            if summary.sweep_is_possible
        ]
