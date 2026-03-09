__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from contextlib import AbstractContextManager
from typing import Self

from httpx import Client

import ua_generator
from httpx import Request


class BaseClient(AbstractContextManager):
    base_url: str

    def __enter__(self) -> Self:
        self._client = Client(
            base_url=self.base_url,
            http2=True,
            event_hooks={
                'request': [self._random_user_agent],
            },
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def _random_user_agent(self, request: Request) -> None:
        ua = ua_generator.generate()
        request.headers['User-Agent'] = ua.text
