from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
import seaborn as sns
import talib
from httpx import Client
from loguru import logger
from matplotlib import pyplot as plt
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from telegram import Telegram

vn30_list = (
    'ACB',
    'BCM',
    'BID',
    'CTG',
    'DGC',
    'FPT',
    'GAS',
    'GVR',
    'HDB',
    'HPG',
    'LPB',
    'MBB',
    'MSN',
    'MWG',
    'PLX',
    'SAB',
    'SHB',
    'SSB',
    'SSI',
    'STB',
    'TCB',
    'TPB',
    'VCB',
    'VHM',
    'VIB',
    'VIC',
    'VJC',
    'VNM',
    'VPB',
    'VRE',
)


class VpsResponse(BaseModel):
    symbol: str
    t: list[int]  # timestamps
    c: list[float]  # closing prices
    o: list[float]  # opening prices
    h: list[float]  # high prices
    l: list[float]  # low prices
    v: list[int]  # volumes


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def fetch_stock_data(symbol: str) -> pd.DataFrame:
    logger.info(f'Fetching data for {symbol}')

    end_time = datetime.now()
    start_time = end_time - timedelta(days=130)
    params = {
        'symbol': symbol,
        'resolution': 'D',
        'from': start_time.timestamp(),
        'to': end_time.timestamp(),
    }

    with Client(base_url='https://histdatafeed.vps.com.vn', http2=True, timeout=10.0) as client:
        resp = client.get('/tradingview/history', params=params)
        resp.raise_for_status()

    data = VpsResponse.model_validate_json(resp.content)

    df = pd.DataFrame(
        {
            'open_time': pd.to_datetime(data.t, unit='s'),
            'open': data.o,
            'high': data.h,
            'low': data.l,
            'close': data.c,
            'volume': data.v,
        }
    )

    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['upper'], df['middle'], df['lower'] = talib.BBANDS(df['close'], timeperiod=14)
    df['ratio'] = (df['close'] - df['middle']) / (df['upper'] - df['middle'])

    logger.info(f'Successfully fetched data for {symbol}')

    return df


def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        data = list(executor.map(fetch_stock_data, vn30_list))

    ohlc_data: dict[str, pd.DataFrame] = {}
    for symbol, df in zip(vn30_list, data):
        ohlc_data[symbol] = df.tail(50)

    ratio_data: dict[str, float] = {}
    for symbol, df in ohlc_data.items():
        ratio_data[symbol] = df['rsi'].iloc[-1]
    rsi_df = pd.DataFrame(
        ratio_data.items(),
        columns=['symbol', 'rsi'],
    )

    down_df = rsi_df[rsi_df['rsi'] < 50].sort_values('rsi', ascending=True)[:5]
    up_df = rsi_df[rsi_df['rsi'] > 50].sort_values('rsi', ascending=False)[:5]

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

            rsi = ohlc_data[symbol]['rsi'].iloc[-1]
            bb = ohlc_data[symbol]['ratio'].iloc[-1]

            sns.lineplot(ohlc_data[symbol], x='open_time', y='close', ax=axes[i, j])
            axes[i, j].set_title(f'{symbol} ({delta_percent:+.2f}%) | RSI: {rsi:.2f} | BB: {bb:.2f}', fontsize=15)
            axes[i, j].tick_params(axis='y', labelsize=10)
            axes[i, j].tick_params(axis='x', labelrotation=30, labelsize=10)

    fig.tight_layout()

    now = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))
    caption = f'VN30 - {now:%Y-%m-%d %H:%M:%S}'

    fig.suptitle(caption, fontsize=20)
    fig.subplots_adjust(top=0.92)

    with BytesIO() as img, Telegram() as tele:
        fig.savefig(img, format='jpg')
        img.seek(0)
        tele.send_photo(img.read(), caption=caption)


if __name__ == '__main__':
    main()
