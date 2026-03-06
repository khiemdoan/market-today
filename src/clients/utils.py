__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import ua_generator
from httpx import Request


def random_user_agent(request: Request) -> None:
    ua = ua_generator.generate()
    request.headers['User-Agent'] = ua.text
