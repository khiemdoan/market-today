import asyncio
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
import pytz
import seaborn as sns
import talib
from httpx import AsyncClient
from matplotlib import pyplot as plt
from pydantic import BaseModel

from telegram import Telegram

vn30_list = (
    'ACB', 'BCM', 'BID', 'CTG', 'DGC', 'FPT',
    'GAS', 'GVR', 'HDB', 'HPG', 'LPB', 'MBB',
    'MSN', 'MWG', 'PLX', 'SAB', 'SHB', 'SSB',
    'SSI', 'STB', 'TCB', 'TPB', 'VCB', 'VHM',
    'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE',
)


class VpsResponse(BaseModel):
    symbol: str
    t: list[int]    # timestamps
    c: list[float]  # closing prices
    o: list[float]  # opening prices
    h: list[float]  # high prices
    l: list[float]  # low prices
    v: list[int]    # volumes


async def fetch_stock_data(client: AsyncClient, symbol: str) -> pd.DataFrame:
    end_time = datetime.now()
    start_time = end_time - timedelta(days=130)
    params = {
        'symbol': symbol,
        'resolution': 'D',
        'from': start_time.timestamp(),
        'to': end_time.timestamp(),
    }
    resp = await client.get('https://histdatafeed.vps.com.vn/tradingview/history', params=params)
    resp.raise_for_status()
    data = resp.json()
    data = VpsResponse.model_validate(data)

    return pd.DataFrame({
        'open_time': pd.to_datetime(data.t, unit='s'),
        'open': data.o,
        'high': data.h,
        'low': data.l,
        'close': data.c,
        'volume': data.v,
    })


def calc_bollinger_bands(close: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return talib.BBANDS(close, timeperiod=20)


async def main():
    async with AsyncClient(base_url='https://histdatafeed.vps.com.vn/', timeout=60.0) as client:
        data = await asyncio.gather(*[fetch_stock_data(client, symbol) for symbol in vn30_list])

    bbands = await asyncio.gather(*[asyncio.to_thread(calc_bollinger_bands, ohlc['close'].to_numpy()) for ohlc in data])
    for df, bband in zip(data, bbands):
        df['upper'] = bband[0]
        df['middle'] = bband[1]
        df['lower'] = bband[2]
        df['ratio'] = (df['close'] - df['middle']) / (df['upper'] - df['middle'])

    ohlc_data: dict[str, pd.DataFrame] = {}
    for symbol, df in zip(vn30_list, data):
        ohlc_data[symbol] = df.tail(50)

    ratio_data: dict[str, float] = {}
    for symbol, df in ohlc_data.items():
        ratio_data[symbol] = df['ratio'].iloc[-1]
    ratio_df = pd.DataFrame(
        ratio_data.items(),
        columns=['symbol', 'ratio'],
    )

    down_df = ratio_df[ratio_df.ratio < 0].sort_values('ratio', ascending=True)[:5]
    up_df = ratio_df[ratio_df.ratio > 0].sort_values('ratio', ascending=False)[:5]

    fig, axes = plt.subplots(5, 2, figsize=(30, 15), sharex=True)

    for i in range(5):
        for j in range(2):
            if j == 0 and i < len(down_df):
                symbol = down_df.iloc[i]['symbol']
            elif j == 1 and i < len(up_df):
                symbol = up_df.iloc[i]['symbol']
            else:
                continue

            last_close = ohlc_data[symbol]['close'].iloc[-2]
            current_close = ohlc_data[symbol]['close'].iloc[-1]
            delta_percent = (current_close - last_close) / last_close * 100

            sns.lineplot(ohlc_data[symbol], x='open_time', y='close', ax=axes[i, j])
            axes[i, j].set_title(f'{symbol} ({delta_percent:+.2f}%)', fontsize=15)
            axes[i, j].tick_params(axis='y', labelsize=10)
            axes[i, j].tick_params(axis='x', labelrotation=30, labelsize=10)

    fig.tight_layout()

    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    caption = f'VN30 - {now:%Y-%m-%d %H:%M:%S}'

    fig.suptitle(caption, fontsize=20)
    fig.subplots_adjust(top=0.92)

    with BytesIO() as img, Telegram() as tele:
        fig.savefig(img, format='jpg')
        img.seek(0)
        tele.send_photo(img.read(), caption=caption)


if __name__ == '__main__':
    asyncio.run(main())
