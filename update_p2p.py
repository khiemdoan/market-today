__author__ = 'KhiemDH'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import httpx
import pandas as pd
from pandas.errors import EmptyDataError

from messenger import send_message
from templates import render


def load_data(file: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(file)
    except (FileNotFoundError, EmptyDataError):
        return pd.DataFrame(columns=['time', 'price']).astype({'time': 'datetime64[s]', 'price': 'int64'})


if __name__ == '__main__':
    now = datetime.now()

    data_dir = Path('data')
    data_dir.mkdir(parents=True, exist_ok=True)
    data_file = data_dir / 'p2p.csv'

    df = load_data(data_file)

    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    payload = {
        'fiat': 'VND',
        'page': 1,
        'rows': 10,
        'tradeType': 'BUY',
        'asset': 'USDT',
        'countries': [],
        'proMerchantAds': False,
        'shieldMerchantAds': False,
        'filterType': 'all',
        'additionalKycVerifyFilter': 0,
        'publisherType': None,
        'payTypes': [],
        'classifies': ['mass', 'profession'],
    }

    resp = httpx.post(url, json=payload)

    data = resp.json()['data']
    price = data[1]['adv']['price']

    row = pd.DataFrame({'time': [now], 'price': [price]})
    row = row.astype({'time': 'datetime64[s]', 'price': 'int64'})
    df = pd.concat([df, row], ignore_index=True)
    df.reset_index()

    df.to_csv(data_file, index=False)

    message = render('p2p.j2', {'time': now, 'price': price})
    result = asyncio.run(send_message(message))

    sys.exit(int(not result))
