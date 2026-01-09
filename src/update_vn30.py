__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import pandas as pd

from clients import DnseClient
from telegram import Telegram
from templates import Render
from utils import generate_graph

if __name__ == '__main__':
    with DnseClient() as client:
        df = client.get_vn30()

    date = df.time.iloc[-1]
    value = df.close.iloc[-1]

    render = Render()
    caption = render(
        'vn30.j2',
        context={
            'date': date,
            'value': value,
            'delta': value - df.close.iloc[-2],
        },
    )

    df['open_time'] = pd.to_datetime(df['time'], unit='s')
    img = generate_graph(df)

    with Telegram() as tele:
        tele.send_photo(img, caption=caption)
