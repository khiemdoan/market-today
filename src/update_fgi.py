__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import sys
from datetime import datetime, timedelta
from io import BytesIO

import httpx
import matplotlib.pyplot as plt
from loguru import logger
from matplotlib.dates import DateFormatter

from dtos import Fgi
from telegram import Telegram

_client = httpx.Client(base_url='https://api.alternative.me', http2=True)


def get_fgi() -> list[Fgi]:
    params = {'limit': 60}
    resp = _client.get('/fng/', params=params)
    data = resp.json()
    return [Fgi(**d) for d in data['data']]


if __name__ == '__main__':
    logger.info('Start collect data')

    data = get_fgi()
    data = data[::-1]
    x = [datetime.fromtimestamp(int(d.timestamp)) for d in data]
    y = [int(d.value) for d in data]
    classification = data[-1].value_classification.replace(' ', '\n')

    fig, ax = plt.subplots()

    ax.plot(x, y)

    ax.set_title(f'Date: {x[-1]:%d/%m/%Y}', fontsize=10, loc='right')

    ax.text(x[-1] + timedelta(days=1), y[-1], f'{y[-1]}', va='center')
    ax.text(x[-1] + timedelta(days=5), y[-1], classification, va='center')

    ax.tick_params(axis='x', labelrotation=25)
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))

    plt.suptitle('Fear & Greed Index')
    plt.tight_layout()

    with BytesIO() as img, Telegram() as tele:
        fig.savefig(img, dpi=400, format='jpg')
        img.seek(0)

        caption = f'FGI ({x[-1]:%d/%m/%Y}): {y[-1]} - {data[-1].value_classification}'
        logger.info(caption)

        result = tele.send_photo(img, caption)
        sys.exit(int(not result))
