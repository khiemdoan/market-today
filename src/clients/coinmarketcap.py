__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Self

from fake_useragent import UserAgent
from httpx import AsyncClient, Client, Request
from pydantic import BaseModel, Field


class Rsi(BaseModel):
    rank: int
    symbol: str
    name: str
    slug: str

    marketCap: float
    volume24h: float
    price: float
    price24h: float

    rsi15m: float
    rsi1h: float
    rsi4h: float
    rsi24h: float
    rsi7d: float


class Status(BaseModel):
    timestamp: datetime
    error_code: int
    error_message: str
    elapsed: int
    credit_count: int


class RsiValue(BaseModel):
    rsi15m: float
    rsi1h: float
    rsi4h: float
    rsi24h: float
    rsi7d: float


class RsiItemResponse(BaseModel):
    id: str
    symbol: str
    slug: str
    name: str
    marketCap: float
    volume24h: float
    price: float
    price24h: float
    rank: int
    rsi: RsiValue


class RsiData(BaseModel):
    data: list[RsiItemResponse]


class RsiResponse(BaseModel):
    data: RsiData


class RsiOverralDetail(BaseModel):
    average_rsi: float = Field(..., alias='averageRsi')
    yesterday: float = Field(..., alias='yesterday')
    days_7_ago: float = Field(..., alias='days7Ago')
    days_30_ago: float = Field(..., alias='days30Ago')
    days_90_ago: float = Field(..., alias='days90Ago')
    oversold_count: int = Field(..., alias='oversoldCount')
    overbought_count: int = Field(..., alias='overboughtCount')
    neutral_count: int = Field(..., alias='neutralCount')
    oversold_percentage: float = Field(..., alias='oversoldPercentage')
    overbought_percentage: float = Field(..., alias='overboughtPercentage')
    neutral_percentage: float = Field(..., alias='neutralPercentage')


class RsiOverall(BaseModel):
    overall: RsiOverralDetail


class RsiOverallResponse(BaseModel):
    data: RsiOverall


class CoinMarketCapClient(AbstractAsyncContextManager):
    def __init__(self) -> None:
        self._ua = UserAgent()

    async def __aenter__(self) -> Self:
        self._client = AsyncClient(
            base_url='https://api.coinmarketcap.com',
            http2=True,
            event_hooks={
                'request': [self._random_user_agent],
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._client.aclose()

    async def _random_user_agent(self, request: Request) -> None:
        request.headers['User-Agent'] = self._ua.random

    async def fetch_overral_rsi(self) -> RsiOverralDetail:
        params = {
            'timeframe': '1h',
            'rsiPeriod': 14,
            'volume24hRange.min': 1000000,
            'marketCapRange.min': 50000000,
        }
        resp = await self._client.get('data-api/v3/cryptocurrency/rsi/heatmap/overall', params=params)
        if not resp.is_success:
            resp.raise_for_status()

        resp = RsiOverallResponse.model_validate_json(resp.content)
        return resp.data.overall

    async def fetch_rsi(self) -> list[Rsi]:
        params = {
            'limit': 10,
            'rsiPeriod': 14,
            'volume24hRange.min': 1000000,
            'marketCapRange.min': 50000000,
            'sort': 'rank',
        }
        resp = await self._client.get('/data-api/v3/cryptocurrency/rsi/heatmap/table', params=params)
        if not resp.is_success:
            resp.raise_for_status()

        resp = RsiResponse.model_validate_json(resp.content)
        return [
            Rsi(
                rank=item.rank,
                symbol=item.symbol,
                name=item.name,
                slug=item.slug,
                marketCap=item.marketCap,
                volume24h=item.volume24h,
                price=item.price,
                price24h=item.price24h,
                rsi15m=item.rsi.rsi15m,
                rsi1h=item.rsi.rsi1h,
                rsi4h=item.rsi.rsi4h,
                rsi24h=item.rsi.rsi24h,
                rsi7d=item.rsi.rsi7d,
            )
            for item in resp.data.data
        ]
