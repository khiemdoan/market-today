__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from contextlib import AbstractContextManager
from typing import Self

from httpx import Client
from pydantic import BaseModel, RootModel

from constants import Interval


class Kline(BaseModel):
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    ignore: float


class Klines(RootModel):
    root: list[Kline]


class BinanceClient(AbstractContextManager):
    def __enter__(self) -> Self:
        self._client = Client(base_url='https://api.binance.com', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def get_klines(self, symbol: str, interval: Interval, limit: int = 500) -> Klines:
        resp = self._client.get('/api/v3/klines', params={'symbol': symbol, 'interval': interval.value, 'limit': limit})
        resp.raise_for_status()

        klines = [
            Kline(
                open_time=k[0],
                open=float(k[1]),
                high=float(k[2]),
                low=float(k[3]),
                close=float(k[4]),
                volume=float(k[5]),
                close_time=k[6],
                quote_asset_volume=float(k[7]),
                number_of_trades=k[8],
                taker_buy_base_asset_volume=float(k[9]),
                taker_buy_quote_asset_volume=float(k[10]),
                ignore=float(k[11]),
            )
            for k in resp.json()
        ]

        return Klines(root=klines)
