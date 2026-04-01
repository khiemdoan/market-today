__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from contextlib import AbstractContextManager
from typing import Self

from niquests import Session
import ua_generator


class BaseClient(AbstractContextManager):
    base_url: str

    def __enter__(self) -> Self:
        self._client = Session(
            base_url=self.base_url,
            resolver=['doh+google://', 'doh+cloudflare://'],
            hooks={
                'pre_request': [self._random_user_agent],
            },
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def _random_user_agent(self, req, *args, **kwargs) -> None:
        ua = ua_generator.generate()
        req.headers['User-Agent'] = ua.text
