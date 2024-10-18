__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from typing import Self

from httpx import Client

from dtos.bybit import Launchpool


class BybitClient:
    def __enter__(self) -> Self:
        self._client = Client(base_url='https://api.bybit.com/', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def get_launchpools(self) -> list[Launchpool]:
        resp = self._client.get('spot/api/launchpool/v1/home')
        return [Launchpool(**d) for d in resp.json()['result']['list']]
