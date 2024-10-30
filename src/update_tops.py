__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime
from math import floor, log

import pandas as pd
from loguru import logger
from prettytable import PrettyTable
from pytz import timezone

from telegram import Telegram
from templates import Render
from trading_view import TradingView


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

    render = Render()
    with TradingView() as client, Telegram() as tele:
        # Top gainers
        data = client.get_top_gainers()
        df = pd.DataFrame([d.model_dump() for d in data])
        df = df[~df['symbol'].str.contains('USD')]
        df['change'] = df['change'].apply(lambda x: f'{x:.2f}%')
        symbols = df['symbol'].to_list()
        table = _craft_table(['Symbol', 'Change'], df)
        message = render('top.j2', context={'title': 'Top gainers', 'time': now, 'symbols': symbols, 'table': table})
        tele.send_message(message, parse_mode='HTML')

        # Top losers
        data = client.get_top_lossers()
        df = pd.DataFrame([d.model_dump() for d in data])
        df = df[~df['symbol'].str.contains('USD')]
        df['change'] = df['change'].apply(lambda x: f'{x:.2f}%')
        symbols = df['symbol'].to_list()
        table = _craft_table(['Symbol', 'Change'], df)
        message = render('top.j2', context={'title': 'Top lossers', 'time': now, 'symbols': symbols, 'table': table})
        tele.send_message(message, parse_mode='HTML')

        # Top tradings
        data = client.get_top_transactions()
        df = pd.DataFrame([d.model_dump() for d in data])
        df = df[~df['symbol'].str.contains('USD')]
        symbols = df['symbol'].to_list()
        table = _craft_table(['Symbol', 'Transaction'], df)
        message = render(
            'top.j2', context={'title': 'Top transaction', 'time': now, 'symbols': symbols, 'table': table}
        )
        tele.send_message(message, parse_mode='HTML')

        # Top volumes
        data = client.get_top_volumes()
        df = pd.DataFrame([d.model_dump() for d in data])
        df = df[~df['symbol'].str.contains('USD')]
        df['volume'] = df['volume'].apply(_format_volume)
        symbols = df['symbol'].to_list()
        table = _craft_table(['Symbol', 'Volume'], df)
        message = render('top.j2', context={'title': 'Top volumes', 'time': now, 'symbols': symbols, 'table': table})
        tele.send_message(message, parse_mode='HTML')
