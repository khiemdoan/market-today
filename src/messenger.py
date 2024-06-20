__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import httpx

from settings import TelegramSettings

_client = httpx.Client(base_url='https://api.telegram.org', http2=True)


def send_message(message: str, preview: bool = False) -> bool:
    settings = TelegramSettings()

    path = f'/bot{settings.bot_token}/sendMessage'
    payload = {
        'chat_id': settings.chat_id,
        'parse_mode': 'HTML',
        'text': message,
        'disable_web_page_preview': not preview,
    }
    try:
        resp = _client.post(path, data=payload)
        return resp.is_success
    except Exception:
        return False
