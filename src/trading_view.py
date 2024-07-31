from copy import copy
from typing import Self

from httpx import Client

from dtos import TopGainer, TopLosser, TopTransaction, TopVolume


class TradingView:
    _path = '/coin/scan'
    _base_payload = {
        'markets': ['coin'],
        'range': [0, 20],
    }

    def __enter__(self) -> Self:
        self._client = Client(base_url='https://scanner.tradingview.com', http2=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def get_top_gainers(self) -> list[TopGainer]:
        payload = copy(self._base_payload)
        payload.update(
            {
                'columns': ['base_currency', '24h_close_change|5'],
                'sort': {'sortBy': '24h_close_change|5', 'sortOrder': 'desc'},
            }
        )
        resp = self._client.post(self._path, json=payload)
        data = resp.json()
        data = [{'symbol': d['d'][0], 'change': d['d'][1]} for d in data['data']]
        return [TopGainer(**d) for d in data]

    def get_top_lossers(self) -> list[TopLosser]:
        payload = copy(self._base_payload)
        payload.update(
            {
                'columns': ['base_currency', '24h_close_change|5'],
                'sort': {'sortBy': '24h_close_change|5', 'sortOrder': 'asc'},
            }
        )
        resp = self._client.post(self._path, json=payload)
        data = resp.json()
        data = [{'symbol': d['d'][0], 'change': d['d'][1]} for d in data['data']]
        return [TopLosser(**d) for d in data]

    def get_top_transactions(self) -> list[TopTransaction]:
        payload = copy(self._base_payload)
        payload.update(
            {
                'columns': ['base_currency', 'txs_count'],
                'sort': {'sortBy': 'txs_count', 'sortOrder': 'desc'},
            }
        )
        resp = self._client.post(self._path, json=payload)
        data = resp.json()
        data = [{'symbol': d['d'][0], 'transaction': d['d'][1]} for d in data['data']]
        return [TopTransaction(**d) for d in data]

    def get_top_volumes(self) -> list[TopVolume]:
        payload = copy(self._base_payload)
        payload.update(
            {
                'columns': ['base_currency', '24h_vol_cmc'],
                'sort': {'sortBy': '24h_vol_cmc', 'sortOrder': 'desc'},
            }
        )
        resp = self._client.post(self._path, json=payload)
        data = resp.json()
        data = [{'symbol': d['d'][0], 'volume': d['d'][1]} for d in data['data']]
        return [TopVolume(**d) for d in data]
