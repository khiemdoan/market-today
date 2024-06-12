__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from telegram import Bot
from telegram.constants import ParseMode

from settings import TelegramSettings


async def send_message(message: str, preview: bool = False) -> bool:
    settings = TelegramSettings()
    bot = Bot(settings.bot_token)
    try:
        await bot.send_message(
            settings.chat_id, message, parse_mode=ParseMode.HTML, disable_web_page_preview=not preview
        )
    except Exception:
        return False
    return True
