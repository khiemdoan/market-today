__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from io import BytesIO
from typing import Self

from httpx import Client

from settings import TelegramSettings


class Telegram:
    def __init__(self) -> None:
        self._settings = TelegramSettings()

    def __enter__(self) -> Self:
        self._client = Client(base_url='https://api.telegram.org', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._client.close()

    def send_message(self, message: str, preview: bool = False) -> bool:
        path = f'/bot{self._settings.bot_token}/sendMessage'
        payload = {
            'chat_id': self._settings.chat_id,
            'parse_mode': 'HTML',
            'text': message,
            'disable_web_page_preview': not preview,
        }
        try:
            resp = self._client.post(path, data=payload)
            return resp.is_success
        except Exception:
            return False

    def send_photo(self, photo: BytesIO, caption: str) -> bool:
        path = f'/bot{self._settings.bot_token}/sendPhoto'
        payload = {'chat_id': self._settings.chat_id, 'caption': caption, 'parse_mode': 'HTML'}
        files = {'photo': photo.read()}
        try:
            resp = self._client.post(path, data=payload, files=files)
            return resp.is_success
        except Exception:
            return False
