__author__ = 'KhiemDH'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import httpx
import pandas as pd
import seaborn as sns
from loguru import logger
from matplotlib import dates
from matplotlib import pyplot as plt
from matplotlib import ticker
from pandas.errors import EmptyDataError

from telegram import Telegram
from templates import Render


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
        'countries': ['VN'],
        'proMerchantAds': False,
        'shieldMerchantAds': False,
        'filterType': 'tradable',
        'additionalKycVerifyFilter': 0,
        'publisherType': None,
        'payTypes': [],
        'classifies': ['mass', 'profession'],
    }

    resp = httpx.post(url, json=payload)

    data = resp.json()['data']
    price = data[1]['adv']['price']

    row = pd.DataFrame({'time': [now], 'price': [price]})
    df = pd.concat([df, row], ignore_index=True)
    df = df.astype({'time': 'datetime64[s]', 'price': 'int64'})
    df.reset_index()

    df.to_csv(data_file, index=False)

    df = df.iloc[-7 * 24 :]

    sns.set_style('whitegrid')

    fig = plt.figure(figsize=(10, 10))
    sns.lineplot(df, x='time', y='price')
    plt.ylabel('Price (VND)')
    plt.gca().xaxis.get_label().set_visible(False)

    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(7))

    with BytesIO() as img, Telegram() as tele:
        fig.savefig(img, format='jpg')
        img.seek(0)

        render = Render()
        caption = render('p2p.j2', {'time': now, 'price': price})
        logger.info(caption)

        result = tele.send_photo(img, caption)
        sys.exit(int(not result))
