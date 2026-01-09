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

    def _get_data(self, params: dict) -> pd.DataFrame:
        resp = self._client.get('/chart-api/v2/ohlcs/index', params=params)
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

    def get_vnindex(self) -> pd.DataFrame:
        to_time = int(datetime.now().timestamp())
        from_time = to_time - 100 * 24 * 60 * 60
        params = {'symbol': 'VNINDEX', 'from': from_time, 'to': to_time, 'resolution': '1D'}
        return self._get_data(params)

    def get_vn30(self) -> pd.DataFrame:
        to_time = int(datetime.now().timestamp())
        from_time = to_time - 100 * 24 * 60 * 60
        params = {'symbol': 'VN30', 'from': from_time, 'to': to_time, 'resolution': '1D'}
        return self._get_data(params)
