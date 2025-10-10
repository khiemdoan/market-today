__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from copy import copy
from datetime import datetime
from typing import Self

import pandas as pd
from httpx import Client

from telegram import Telegram
from utils import generate_graph
from templates import Render


class StockClient:
    def __enter__(self) -> Self:
        self._client = Client(base_url='https://apipubaws.tcbs.com.vn', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    _params = {
        'resolution': 'D',
        'type': 'index',
        'countBack': 100,
    }

    def _get_data(self, params: dict) -> pd.DataFrame:
        data = self._client.get('/stock-insight/v2/stock/bars-long-term', params=params).json()
        df = pd.DataFrame(data['data'])
        df.rename(columns={'tradingDate': 'open_time'}, inplace=True)
        df['open_time'] = pd.to_datetime(df['open_time'])
        return df

    def get_vnindex(self) -> pd.DataFrame:
        params = copy(self._params)
        params.update({'ticker': 'VNINDEX', 'to': int(datetime.now().timestamp())})
        return self._get_data(params)

    def get_vn30(self) -> pd.DataFrame:
        params = copy(self._params)
        params.update({'ticker': 'VN30', 'to': int(datetime.now().timestamp())})
        return self._get_data(params)


if __name__ == '__main__':
    with StockClient() as client:
        data = client.get_vn30()

    date = data.open_time.iloc[-1]
    value = data.close.iloc[-1]

    render = Render()
    caption = render('vn30.j2', context={
        'date': date,
        'value': value,
        'delta': value - data.close.iloc[-2],
    })
    img = generate_graph(data)

    with Telegram() as tele:
        tele.send_photo(img, caption=caption)
