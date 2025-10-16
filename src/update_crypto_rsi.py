__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import asyncio
from datetime import datetime
from io import BytesIO

import pandas as pd
import pytz
import seaborn as sns
from matplotlib import pyplot as plt

from clients import CoinMarketCapClient
from telegram import Telegram
from templates import Render


async def main() -> None:
    async with CoinMarketCapClient() as client:
        overall = await client.fetch_overral_rsi()
        data = await client.fetch_rsi()

    df = pd.DataFrame([row.model_dump() for row in data])

    sns.set_style('whitegrid')
    fig, axes = plt.subplots(2, figsize=(15, 10))

    sns.scatterplot(x='symbol', y='rsi1h', data=df, ax=axes[0])
    axes[0].set_ylim(0, 100)
    axes[0].set_xlabel('')
    axes[0].set_ylabel('')

    df = df[['symbol', 'volume24h', 'price', 'price24h', 'rsi15m', 'rsi1h', 'rsi4h', 'rsi24h', 'rsi7d']]

    df['volume24h'] = df['volume24h'].apply(lambda x: f'{x:.2f}')
    df['price'] = df['price'].apply(lambda x: f'{x:.2f}')
    df['price24h'] = df['price24h'].apply(lambda x: f'{x:.2f}%')
    df['rsi15m'] = df['rsi15m'].apply(lambda x: f'{x:.2f}')
    df['rsi1h'] = df['rsi1h'].apply(lambda x: f'{x:.2f}')
    df['rsi4h'] = df['rsi4h'].apply(lambda x: f'{x:.2f}')
    df['rsi24h'] = df['rsi24h'].apply(lambda x: f'{x:.2f}')
    df['rsi7d'] = df['rsi7d'].apply(lambda x: f'{x:.2f}')

    # display df in table for axes[1]
    axes[1].axis('off')
    table = axes[1].table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    conclude = 'Neutral'
    if overall.average_rsi < 30:
        conclude = 'Oversold'
    elif overall.average_rsi > 70:
        conclude = 'Overbought'

    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    render = Render()
    caption = render(
        'crypto_rsi.j2',
        context={
            'time': now,
            'average': overall.average_rsi,
            'oversold_percentage': overall.oversold_percentage,
            'overbought_percentage': overall.overbought_percentage,
            'conclude': conclude,
        },
    )

    with BytesIO() as img, Telegram() as tele:
        fig.savefig(img, format='jpg')
        img.seek(0)
        tele.send_photo(img.read(), caption=caption)


if __name__ == '__main__':
    asyncio.run(main())
