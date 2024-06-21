__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import logging
from copy import copy
from datetime import datetime
from math import floor, log

import httpx
import pandas as pd
from prettytable import PrettyTable
from pytz import timezone

from dtos import TopGainer, TopLosser, TopTransaction, TopVolume
from messenger import send_message
from templates import render

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


_client = httpx.Client(base_url='https://scanner.tradingview.com', http2=True)
_path = '/coin/scan'
_base_payload = {
    'markets': ['coin'],
    'range': [0, 20],
}


def get_top_gainers() -> list[TopGainer]:
    payload = copy(_base_payload)
    payload.update({
        'columns': ['base_currency', '24h_close_change|5'],
        'sort': {'sortBy': '24h_close_change|5', 'sortOrder': 'desc'},
    })
    resp = _client.post(_path, json=payload)
    data = resp.json()
    data = [{'symbol': d['d'][0], 'change': d['d'][1]} for d in data['data']]
    return [TopGainer(**d) for d in data]


def get_top_lossers() -> list[TopLosser]:
    payload = copy(_base_payload)
    payload.update({
        'columns': ['base_currency', '24h_close_change|5'],
        'sort': {'sortBy': '24h_close_change|5', 'sortOrder': 'asc'},
    })
    resp = _client.post(_path, json=payload)
    data = resp.json()
    data = [{'symbol': d['d'][0], 'change': d['d'][1]} for d in data['data']]
    return [TopLosser(**d) for d in data]


def get_top_transactions() -> list[TopTransaction]:
    payload = copy(_base_payload)
    payload.update({
        'columns': ['base_currency', 'txs_count'],
        'sort': {'sortBy': 'txs_count', 'sortOrder': 'desc'},
    })
    resp = _client.post(_path, json=payload)
    data = resp.json()
    data = [{'symbol': d['d'][0], 'transaction': d['d'][1]} for d in data['data']]
    return [TopTransaction(**d) for d in data]


def get_top_volumes() -> list[TopVolume]:
    payload = copy(_base_payload)
    payload.update({
        'columns': ['base_currency', '24h_vol_cmc'],
        'sort': {'sortBy': '24h_vol_cmc', 'sortOrder': 'desc'},
    })
    resp = _client.post(_path, json=payload)
    data = resp.json()
    data = [{'symbol': d['d'][0], 'volume': d['d'][1]} for d in data['data']]
    return [TopVolume(**d) for d in data]


def _craft_table(fields: list[str], data: pd.DataFrame) -> str:
    table = PrettyTable()
    table.field_names = fields
    table.align = 'r'
    for _, row in data.iterrows():
        table.add_row([row.iloc[0], row.iloc[1]])

    return str(table)


def _format_volume(number) -> str:
    units = ['', 'K', 'M', 'B', 'T', 'Q']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return f'{(number / k**magnitude):.2f}{units[magnitude]}'


if __name__ == '__main__':
    logger.info('Start collect data')

    now = datetime.now(tz=timezone('Asia/Ho_Chi_Minh'))

    # Top gainers
    data = get_top_gainers()
    df = pd.DataFrame([d.model_dump() for d in data])
    df = df[~df['symbol'].str.contains('USD')]
    df['change'] = df['change'].apply(lambda x: '{:.2f}%'.format(x))
    symbols = df['symbol'].to_list()
    table = _craft_table(['Symbol', 'Change'], df)
    message = render('top.j2', context={'title': 'Top gainers', 'time': now, 'symbols': symbols, 'table': table})
    send_message(message)

    # Top losers
    data = get_top_lossers()
    df = pd.DataFrame([d.model_dump() for d in data])
    df = df[~df['symbol'].str.contains('USD')]
    df['change'] = df['change'].apply(lambda x: '{:.2f}%'.format(x))
    symbols = df['symbol'].to_list()
    table = _craft_table(['Symbol', 'Change'], df)
    message = render('top.j2', context={'title': 'Top lossers', 'time': now, 'symbols': symbols, 'table': table})
    send_message(message)

    # Top tradings
    data = get_top_transactions()
    df = pd.DataFrame([d.model_dump() for d in data])
    df = df[~df['symbol'].str.contains('USD')]
    symbols = df['symbol'].to_list()
    table = _craft_table(['Symbol', 'Transaction'], df)
    message = render('top.j2', context={'title': 'Top transaction', 'time': now, 'symbols': symbols, 'table': table})
    send_message(message)

    # Top volumes
    data = get_top_volumes()
    df = pd.DataFrame([d.model_dump() for d in data])
    df = df[~df['symbol'].str.contains('USD')]
    df['volume'] = df['volume'].apply(_format_volume)
    symbols = df['symbol'].to_list()
    table = _craft_table(['Symbol', 'Volume'], df)
    message = render('top.j2', context={'title': 'Top volumes', 'time': now, 'symbols': symbols, 'table': table})
    send_message(message)
