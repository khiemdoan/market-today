__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime
from typing import Self

import pandas as pd
from httpx import Client

from telegram import Telegram
from utils import generate_graph


class StockClient:
    def __enter__(self) -> Self:
        self._client = Client(base_url='https://apipubaws.tcbs.com.vn', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def get_vnindex(self) -> pd.DataFrame:
        params = {
            'resolution': 'D',
            'ticker': 'VNINDEX',
            'type': 'index',
            'to': int(datetime.now().timestamp()),
            'countBack': 100,
        }
        data = self._client.get('/stock-insight/v2/stock/bars-long-term', params=params).json()
        df = pd.DataFrame(data['data'])
        df.rename(columns={'tradingDate': 'open_time'}, inplace=True)
        df['open_time'] = pd.to_datetime(df['open_time'])
        return df


if __name__ == '__main__':
    with StockClient() as client:
        data = client.get_vnindex()

    date = data.open_time.iloc[-1]
    value = data.close.iloc[-1]

    caption = f'🇻🇳 {date:%d-%m-%Y} VN-Index: {value}'
    img = generate_graph(data)

    with Telegram() as tele:
        tele.send_photo(img, caption=caption)
