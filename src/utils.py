__author__ = 'KhiemDH'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import timedelta
from io import BytesIO

import pandas as pd
import pandas_ta as ta
from matplotlib import pyplot as plt


def generate_graph(klines: pd.DataFrame) -> bytes:
    up_color = 'lime'
    down_color = 'tomato'
    body_width = timedelta(hours=15)
    shadow_width = timedelta(hours=5)

    klines['volume_sma'] = ta.sma(klines.volume)

    klines = klines.iloc[-50:]
    price = klines.close.iloc[-1]

    up = klines[klines.close > klines.open]
    down = klines[klines.close <= klines.open]

    fig, axes = plt.subplots(2, figsize=(30, 15), sharex=True)

    if len(up) > 0:
        axes[0].bar(up.open_time, up.close - up.open, body_width, up.open, color=up_color)
        axes[0].bar(up.open_time, up.high - up.low, shadow_width, up.low, color=up_color)
        axes[1].bar(up.open_time, up.volume, body_width, color=up_color)

    if len(down) > 0:
        axes[0].bar(down.open_time, down.open - down.close, body_width, down.close, color=down_color)
        axes[0].bar(down.open_time, down.high - down.low, shadow_width, down.low, color=down_color)
        axes[1].bar(down.open_time, down.volume, body_width, color=down_color)

    axes[0].axhline(y=price, color='darkviolet')

    delta = klines.high.max() - klines.low.min()
    top_price = klines.high.max() + delta * 0.05
    bottom_price = klines.low.min() - delta * 0.05

    axes[0].set_ylim(bottom_price, top_price)

    axes[1].plot(klines.open_time, klines.volume_sma, color='blue')

    axes[0].tick_params(axis='y', labelsize=15)
    axes[1].tick_params(axis='y', labelsize=15)
    axes[1].tick_params(axis='x', labelrotation=30, labelsize=15)

    plt.subplots_adjust(left=0.03, bottom=0.05, right=0.97, top=0.95, wspace=0.05, hspace=0.07)

    with BytesIO() as img:
        fig.savefig(img, format='jpg')
        img.seek(0)
        return img.read()
