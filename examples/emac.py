from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue

from qsforex.backtest.practice import Practice
from qsforex.execution.execution import OANDAExecutionHandler
from qsforex.portfolio.portfolio import Portfolio
from qsforex import settings
from qsforex.strategy.strategy import ExponentialMovingAverageCrossStrategy
from qsforex.data.streaming import StreamingForexPrices

if __name__ == "__main__":
    # Trade on EUR/USD
    pairs = ["EURUSD"]

    # Create the strategy parameters for the
    # ExponentialMovingAverageCrossStrategy
    strategy_params = {
        "short_window": 500,
        "long_window": 2000
    }
    events = queue.Queue()
    data_handler = StreamingForexPrices(
        settings.API_DOMAIN,
        settings.ACCESS_TOKEN,
        settings.ACCOUNT_ID,
        pairs,
        events
    )
    execution = OANDAExecutionHandler(
        settings.API_DOMAIN,
        settings.ACCESS_TOKEN,
        settings.ACCOUNT_ID
    )
    # Create and execute the back test
    practice = Practice(
        pairs, data_handler,
        ExponentialMovingAverageCrossStrategy, strategy_params,
        Portfolio, execution, events,
        equity=settings.EQUITY
    )
    practice.simulate_trading()
