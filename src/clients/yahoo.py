from contextlib import AbstractContextManager
from typing import Self

import pandas as pd
import yfinance as yf


class YahooClient(AbstractContextManager):
    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return

    def _get_data(self, symbol: str, period: str = '2mo') -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period).reset_index()

        return history.rename(
            columns={
                'Date': 'open_time',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
            }
        )

    def get_gold(self, period: str = '2mo') -> pd.DataFrame:
        return self._get_data('GC=F', period)

    def get_oil(self, period: str = '2mo') -> pd.DataFrame:
        return self._get_data('CL=F', period)
