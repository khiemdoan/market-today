__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from clients import DnseClient
from graph import draw_klines
from telegram import Telegram
from templates import Render

if __name__ == '__main__':
    with DnseClient() as client:
        df = client.get_vn30()

    date = df.open_time.iloc[-1]
    value = df.close.iloc[-1]
    value_prev = df.close.iloc[-2]

    render = Render()
    caption = render(
        'vn30.j2',
        context={
            'date': date,
            'value': value,
            'delta': value - value_prev,
        },
    )

    img = draw_klines(df)
    with open('vn30.png', 'wb') as f:
        f.write(img)

    # with Telegram() as tele:
    #     tele.send_photo(img, caption=caption)
