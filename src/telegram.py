__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import re
from typing import Self

from httpx import Client, Response

from settings import TelegramSettings


class Telegram:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"

    def __init__(self) -> None:
        self._settings = TelegramSettings()

    def __enter__(self) -> Self:
        self._client = Client(base_url='https://api.telegram.org', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def send_message(self, text: str, preview: bool = False) -> Response:
        text = re.sub(f"([{re.escape(self.escape_chars)}])", r"\\\1", text)
        path = f'/bot{self._settings.bot_token}/sendMessage'
        payload = {
            'chat_id': self._settings.chat_id,
            'text': text,
            'parse_mode': 'MarkdownV2',
            'disable_web_page_preview': not preview,
        }
        return self._client.post(path, data=payload)

    def send_photo(self, photo: bytes, caption: str) -> Response:
        path = f'/bot{self._settings.bot_token}/sendPhoto'
        payload = {
            'chat_id': self._settings.chat_id,
            'caption': caption,
            'parse_mode': 'HTML',
        }
        files = {'photo': photo}
        return self._client.post(path, data=payload, files=files)
