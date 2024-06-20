__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from .base import Base


class TopGainer(Base):
    symbol: str
    change: float


class TopLosser(Base):
    symbol: str
    change: float


class TopTransaction(Base):
    symbol: str
    transaction: int


class TopVolume(Base):
    symbol: str
    volume: float
