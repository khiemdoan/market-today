from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Self

import pandas as pd
from httpx import Client
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import random_user_agent


class OhlcData(BaseModel):
    symbol: str
    time: list[datetime] = Field(alias='t')
    open: list[float] = Field(alias='o')
    high: list[float] = Field(alias='h')
    low: list[float] = Field(alias='l')
    close: list[float] = Field(alias='c')
    volume: list[int] = Field(alias='v')


class VciClient(AbstractContextManager):
    def __enter__(self) -> Self:
        self._client = Client(
            base_url='https://trading.vietcap.com.vn',
            http2=True,
            event_hooks={
                'request': [random_user_agent],
            },
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def get_vn30(self) -> pd.DataFrame:
        headers = {
            'Referer': 'https://trading.vietcap.com.vn/price-board'
        }
        to_time = datetime.now()
        from_time = to_time - timedelta(days=100)
        data = {
            'timeFrame': 'ONE_DAY',
            'symbols': ['VN30'],
            'from': int(from_time.timestamp()),
            'to': int(to_time.timestamp()),
        }
        resp = self._client.post('/api/chart/OHLCChart/gap', headers=headers, json=data)
        print(f'get_vn30: {resp.request.method} {resp.url} status_code={resp.status_code}')
        resp.raise_for_status()

        data = resp.json()
        for d in data:
            if d['symbol'] == 'VN30':
                ohlc = OhlcData.model_validate(d)
                df = pd.DataFrame(
                    {
                        'open_time': ohlc.time,
                        'open': ohlc.open,
                        'high': ohlc.high,
                        'low': ohlc.low,
                        'close': ohlc.close,
                        'volume': ohlc.volume,
                    }
                )
                df['open_time'] = pd.to_datetime(df['open_time']).dt.tz_localize(None)
                df['volume'] = df['volume'].astype('float64')
                return df

        raise ValueError('VN30 data not found')
