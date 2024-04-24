__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from telegram import Bot
from telegram.constants import ParseMode


class TelegramSettings(BaseSettings):
    bot_token: str
    chat_id: str

    model_config = SettingsConfigDict(extra='ignore', env_prefix='TELEGRAM_')


def get_telegram_settings() -> TelegramSettings:
    try:
        return TelegramSettings()
    except ValidationError:
        pass

    return TelegramSettings(_env_file='.env')


async def send_message(message: str, preview: bool = False) -> bool:
    settings = get_telegram_settings()
    bot = Bot(settings.bot_token)
    try:
        await bot.send_message(settings.chat_id, message, parse_mode=ParseMode.HTML, disable_web_page_preview=not preview)
    except Exception:
        return False
    return True
