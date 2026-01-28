from contextlib import AbstractContextManager
from typing import Self

import polars as pl
import yfinance as yf


class CommoditiesClient(AbstractContextManager):
    GOLD_SYMBOL = "GC=F"
    OIL_SYMBOL = "CL=F"

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def _get_data(self, symbol: str, period: str = "2mo") -> pl.DataFrame:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period).reset_index()

        df = pl.from_pandas(
            history.rename(columns={
                "Date": "open_time",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            })
        )

        return (
            df.select([
                pl.col("open_time").cast(pl.Datetime("us")),
                pl.col("open").cast(pl.Float64),
                pl.col("high").cast(pl.Float64),
                pl.col("low").cast(pl.Float64),
                pl.col("close").cast(pl.Float64),
                pl.col("volume").cast(pl.Float64),
            ])
            .drop_nulls()
            .sort("open_time")
        )

    def get_gold(self, period: str = "2mo") -> pl.DataFrame:
        return self._get_data(self.GOLD_SYMBOL, period)

    def get_oil(self, period: str = "2mo") -> pl.DataFrame:
        return self._get_data(self.OIL_SYMBOL, period)
