from contextlib import AbstractContextManager
from datetime import datetime
from typing import Self

import pandas as pd
from httpx import Client
from pydantic import BaseModel, Field


class OhlcResponse(BaseModel):
    time: list[datetime] = Field(alias='t')
    open: list[float] = Field(alias='o')
    high: list[float] = Field(alias='h')
    low: list[float] = Field(alias='l')
    close: list[float] = Field(alias='c')
    volume: list[int] = Field(alias='v')


class DnseClient(AbstractContextManager):
    def __enter__(self) -> Self:
        self._client = Client(base_url='https://api.dnse.com.vn', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def _get_data(self, url: str, params: dict) -> pd.DataFrame:
        resp = self._client.get(url, params=params)
        resp.raise_for_status()

        print(resp.url)

        data = OhlcResponse.model_validate_json(resp.content)

        return pd.DataFrame(
            {
                'time': data.time,
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume,
            }
        )

    def _get_data_index(self, params: dict) -> pd.DataFrame:
        return self._get_data('/chart-api/v2/ohlcs/index', params)

    def _get_data_stock(self, params: dict) -> pd.DataFrame:
        return self._get_data('/chart-api/v2/ohlcs/stock', params)

    def get_vnindex(self) -> pd.DataFrame:
        to_time = int(datetime.now().timestamp())
        from_time = to_time - 100 * 24 * 60 * 60
        params = {'symbol': 'VNINDEX', 'from': from_time, 'to': to_time, 'resolution': '1D'}
        return self._get_data_index(params)

    def get_vn30(self) -> pd.DataFrame:
        to_time = int(datetime.now().timestamp())
        from_time = to_time - 100 * 24 * 60 * 60
        params = {'symbol': 'VN30', 'from': from_time, 'to': to_time, 'resolution': '1D'}
        return self._get_data_index(params)

    def get_stock(self, symbol: str, days: int = 130) -> pd.DataFrame:
        to_time = int(datetime.now().timestamp())
        from_time = to_time - days * 24 * 60 * 60
        params = {'symbol': symbol, 'from': from_time, 'to': to_time, 'resolution': '1D'}
        return self._get_data_stock(params)
