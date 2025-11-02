__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime, timedelta
from io import BytesIO
from typing import Self

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fake_useragent import UserAgent
from httpx import Client, Request
from loguru import logger
from matplotlib.dates import DateFormatter
from pydantic import BaseModel, Field

from telegram import Telegram
from templates import Render


class Fgi(BaseModel):
    score: int
    name: str
    timestamp: datetime
    btc_price: float = Field(alias='btcPrice')
    btc_volume: float = Field(alias='btcVolume')


class HistoricalValue(BaseModel):
    score: int
    name: str
    timestamp: int


class HistoricalValues(BaseModel):
    now: HistoricalValue
    yesterday: HistoricalValue
    lastWeek: HistoricalValue
    lastMonth: HistoricalValue
    yearlyHigh: HistoricalValue
    yearlyLow: HistoricalValue


class Data(BaseModel):
    dataList: list[Fgi]
    historicalValues: HistoricalValues


class Status(BaseModel):
    timestamp: datetime
    error_code: int
    error_message: str
    elapsed: int
    credit_count: int


class StatusResponse(BaseModel):
    status: Status


class FgiResponse(BaseModel):
    data: Data


class FgiClient:
    def __init__(self) -> None:
        self._ua = UserAgent()

    def __enter__(self) -> Self:
        self._client = Client(
            base_url='https://api.coinmarketcap.com',
            http2=True,
            event_hooks={
                'request': [self._random_user_agent],
            },
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def _random_user_agent(self, request: Request) -> None:
        request.headers['User-Agent'] = self._ua.random

    def get(self) -> list[Fgi]:
        end = datetime.now()
        start = end - timedelta(days=30)
        params = {
            'start': int(start.timestamp()),
            'end': int(end.timestamp()),
        }
        resp = self._client.get('/data-api/v3/fear-greed/chart', params=params)
        if not resp.is_success:
            resp.raise_for_status()

        status_resp = StatusResponse.model_validate_json(resp.content)
        if status_resp.status.error_code != 0:
            raise Exception(status_resp.status.error_message)

        fgi_resp = FgiResponse.model_validate_json(resp.content)
        return fgi_resp.data.dataList


if __name__ == '__main__':
    logger.info('Start collect data')

    with FgiClient() as client:
        data = client.get()

    df = pd.DataFrame(
        [d.model_dump() for d in data],
    )
    time = data[-1].timestamp
    value = data[-1].score
    classification = data[-1].name

    sns.set_theme(style='darkgrid')

    ax = sns.lineplot(data=df, x='timestamp', y='score')
    ax.set_title(f'Date: {time:%d/%m/%Y}', fontsize=10, loc='right')

    ax.text(time + timedelta(days=1), value, f'{value}', va='center')
    ax.text(time + timedelta(days=5), value, classification.replace(' ', '\n'), va='center')

    ax.tick_params(axis='x', labelrotation=25)
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))

    plt.suptitle('Fear & Greed Index')
    plt.tight_layout()

    with BytesIO() as img, Telegram() as tele:
        plt.savefig(img, dpi=400, format='jpg')
        img.seek(0)

        render = Render()
        caption = render('fgi.j2', {'time': time, 'value': value, 'classification': classification})
        logger.info(caption)

        tele.send_photo(img, caption, parse_mode='HTML')
