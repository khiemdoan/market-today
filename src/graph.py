__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime
from io import BytesIO

import pandas as pd
import pandera.pandas as pa
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class Kline(pa.DataFrameModel):
    open_time: datetime = pa.Field()
    open: float = pa.Field(ge=0)
    high: float = pa.Field(ge=0)
    low: float = pa.Field(ge=0)
    close: float = pa.Field(ge=0)
    volume: float = pa.Field(ge=0)


def draw_klines(klines: pd.DataFrame) -> bytes:
    klines = Kline.validate(klines)

    up_color = 'lime'
    down_color = 'tomato'
    delta_time = klines['open_time'].diff().max()
    body_width = delta_time * 0.6
    shadow_width = delta_time * 0.2

    klines['volume_sma'] = klines['volume'].rolling(window=10).mean()

    klines = klines.tail(50)
    price = klines['close'].tail(1).item()
    up = klines[klines['close'] > klines['open']]
    down = klines[klines['close'] <= klines['open']]

    fig: Figure
    axes: tuple[Axes, Axes]
    fig, axes = plt.subplots(2, figsize=(30, 15), sharex=True)

    if len(up) > 0:
        axes[0].bar(up['open_time'], up['close'] - up['open'], body_width, up['open'], color=up_color)
        axes[0].bar(up['open_time'], up['high'] - up['low'], shadow_width, up['low'], color=up_color)
        axes[1].bar(up['open_time'], up['volume'], body_width, color=up_color)

    if len(down) > 0:
        axes[0].bar(down['open_time'], down['open'] - down['close'], body_width, down['close'], color=down_color)
        axes[0].bar(down['open_time'], down['high'] - down['low'], shadow_width, down['low'], color=down_color)
        axes[1].bar(down['open_time'], down['volume'], body_width, color=down_color)

    axes[0].axhline(y=price, color='darkviolet')

    high = klines['high'].max()
    low = klines['low'].min()

    delta = high - low
    top_price = high + delta * 0.05
    bottom_price = low - delta * 0.05

    axes[0].set_ylim(bottom_price, top_price)

    axes[1].plot(klines['open_time'], klines['volume_sma'], color='blue')

    axes[0].tick_params(axis='y', labelsize=15)
    axes[1].tick_params(axis='y', labelsize=15)
    axes[1].tick_params(axis='x', labelrotation=30, labelsize=15)

    plt.subplots_adjust(
        left=0.03,
        bottom=0.1,
        right=0.97,
        top=0.95,
        wspace=0.05,
        hspace=0.07,
    )

    with BytesIO() as img:
        fig.savefig(img, format='jpg')
        img.seek(0)
        return img.read()
