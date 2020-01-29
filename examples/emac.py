from __future__ import print_function

from qsforex.backtest.backtest import Backtest
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

    # Create and execute the back test
    back_test = Backtest(
        pairs, StreamingForexPrices,
        ExponentialMovingAverageCrossStrategy, strategy_params,
        Portfolio, OANDAExecutionHandler,
        equity=settings.EQUITY
    )
    back_test.simulate_trading()
