__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime
from io import BytesIO

import patito as pt
import polars as pl
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class Kline(pt.Model):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def draw_klines(klines: pl.DataFrame) -> bytes:
    klines = Kline.validate(klines, drop_superfluous_columns=True)

    up_color = 'lime'
    down_color = 'tomato'
    delta_time = klines.select(pl.col('open_time').diff().max()).item()
    body_width = delta_time * 0.6
    shadow_width = delta_time * 0.2

    klines = klines.with_columns(pl.col('volume').rolling_mean(10).alias('volume_sma'))

    klines = klines.tail(50)
    price = klines.select(pl.col('close').tail(1)).item()

    up = klines.filter(pl.col('close') > pl.col('open'))
    down = klines.filter(pl.col('close') <= pl.col('open'))

    fig: Figure
    axes: tuple[Axes, Axes]
    fig, axes = plt.subplots(2, figsize=(30, 15), sharex=True)

    if up.height > 0:
        axes[0].bar(up['open_time'], up['close'] - up['open'], body_width, up['open'], color=up_color)
        axes[0].bar(up['open_time'], up['high'] - up['low'], shadow_width, up['low'], color=up_color)
        axes[1].bar(up['open_time'], up['volume'], body_width, color=up_color)

    if down.height > 0:
        axes[0].bar(down['open_time'], down['open'] - down['close'], body_width, down['close'], color=down_color)
        axes[0].bar(down['open_time'], down['high'] - down['low'], shadow_width, down['low'], color=down_color)
        axes[1].bar(down['open_time'], down['volume'], body_width, color=down_color)

    axes[0].axhline(y=price, color='darkviolet')

    high = klines.select(pl.col('high').max()).item()
    low = klines.select(pl.col('low').min()).item()

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
