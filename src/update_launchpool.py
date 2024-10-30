__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from loguru import logger

from clients import BybitClient
from telegram import Telegram
from templates import Render

if __name__ == '__main__':
    logger.info('Start updating launchpool')

    with BybitClient() as client:
        launchpools = client.get_launchpools()

    render = Render()
    context = {'launchpools': launchpools}
    text = render('launchpool.j2', context)
    text = text.strip()
    print(text)

    with Telegram() as tele:
        resp = tele.send_message(text)
        print(resp)
