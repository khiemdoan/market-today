__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import asyncio
import logging
from datetime import datetime
from math import floor, log

import httpx
import pandas as pd
from prettytable import PrettyTable
from pytz import timezone

from dtos import Ticker
from messenger import send_message
from templates import arender

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info('Start collect data')

    now = datetime.now(tz=timezone('Asia/Ho_Chi_Minh'))

    async with httpx.AsyncClient(base_url='https://fapi.binance.com', http2=True) as client:
        resp = await client.get('/fapi/v1/ticker/24hr')
        data = resp.json()
        tickers = [Ticker(**d) for d in data]

    tickers = pd.DataFrame([t.model_dump() for t in tickers])

    # Top gainers
    tops = tickers[['symbol', 'price_change_percent']].sort_values(by='price_change_percent', ascending=False)
    tops = tops.iloc[:10, :]
    logger.info(f'Top gainer: {tops.iloc[0, 0]} {tops.iloc[0, 1]}%')

    symbols = tops['symbol'].to_list()
    table = _craft_table(['Symbol', 'Change'], tops)
    message = await arender('top.j2', context={'title': 'Top gainers', 'time': now, 'symbols': symbols, 'table': table})
    await send_message(message)

    # Top losers
    tops = tickers[['symbol', 'price_change_percent']].sort_values(by='price_change_percent')
    tops = tops.iloc[:10, :]
    logger.info(f'Top loser: {tops.iloc[0, 0]} {tops.iloc[0, 1]}%')

    symbols = tops['symbol'].to_list()
    table = _craft_table(['Symbol', 'Change'], tops)
    message = await arender('top.j2', context={'title': 'Top losers', 'time': now, 'symbols': symbols, 'table': table})
    await send_message(message)

    # Top tradings
    tops = tickers[['symbol', 'count']].sort_values(by='count', ascending=False)
    tops = tops.iloc[:10, :]
    logger.info(f'Top tradings: {tops.iloc[0, 0]} {tops.iloc[0, 1]}')

    symbols = tops['symbol'].to_list()
    table = _craft_table(['Symbol', 'Trade'], tops)
    message = await arender(
        'top.j2', context={'title': 'Top tradings', 'time': now, 'symbols': symbols, 'table': table}
    )
    await send_message(message)

    # Top volumes
    tops = tickers[['symbol', 'quote_volume']].sort_values(by='quote_volume', ascending=False)
    tops = tops.iloc[:10, :]
    tops['quote_volume'] = tops['quote_volume'].apply(_format_volume)
    logger.info(f'Top volumes: {tops.iloc[0, 0]} ${tops.iloc[0, 1]}')

    symbols = tops['symbol'].to_list()
    table = _craft_table(['Symbol', 'Volume'], tops)
    message = await arender('top.j2', context={'title': 'Top volumes', 'time': now, 'symbols': symbols, 'table': table})
    await send_message(message)


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
    asyncio.run(main())
