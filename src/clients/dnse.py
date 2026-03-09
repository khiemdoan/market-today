from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseClient


class OhlcResponse(BaseModel):
    time: list[datetime] = Field(alias='t')
    open: list[float] = Field(alias='o')
    high: list[float] = Field(alias='h')
    low: list[float] = Field(alias='l')
    close: list[float] = Field(alias='c')
    volume: list[int] = Field(alias='v')


class DnseClient(BaseClient):
    base_url: str = 'https://api.dnse.com.vn'

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _get_data(self, url: str, params: dict) -> pd.DataFrame:
        resp = self._client.get(url, params=params)
        print(resp.url)
        resp.raise_for_status()

        data = OhlcResponse.model_validate_json(resp.content)

        df = pd.DataFrame(
            {
                'time': data.time,
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume,
            }
        )
        df['open_time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
        df['volume'] = df['volume'].astype('float64')
        return df

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
