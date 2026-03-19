__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime, timedelta

import pandas as pd
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseClient


class OhlcData(BaseModel):
    symbol: str
    time: list[datetime] = Field(alias='t')
    open: list[float] = Field(alias='o')
    high: list[float] = Field(alias='h')
    low: list[float] = Field(alias='l')
    close: list[float] = Field(alias='c')
    volume: list[int] = Field(alias='v')


class VciClient(BaseClient):
    base_url: str = 'https://trading.vietcap.com.vn'

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

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def get_stocks(self, symbols: list[str], days: int = 100) -> dict[str, pd.DataFrame]:
        headers = {
            'Referer': 'https://trading.vietcap.com.vn/priceboard'
        }
        data = {
            'timeFrame': 'ONE_DAY',
            'symbols': symbols,
            'countBack': days,
            'to': int(datetime.now().timestamp()),
        }
        resp = self._client.post('/api/chart/OHLCChart/gap-chart', headers=headers, json=data)
        resp.raise_for_status()

        data = resp.json()
        data = {
            d['symbol']: OhlcData.model_validate(d)
            for d in data
        }

        data = {
            symbol: pd.DataFrame(
                {
                    'open_time': ohlc.time,
                    'open': ohlc.open,
                    'high': ohlc.high,
                    'low': ohlc.low,
                    'close': ohlc.close,
                    'volume': ohlc.volume,
                }
            )
            for symbol, ohlc in data.items()
        }

        return {
            symbol: df.assign(
                open_time=pd.to_datetime(df['open_time']).dt.tz_localize(None),
                volume=df['volume'].astype('float64'),
            )
            for symbol, df in data.items()
        }
