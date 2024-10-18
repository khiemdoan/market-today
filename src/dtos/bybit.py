__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from datetime import datetime

from .base import Base


class StakePool(Base):
    stake_coin: str
    apr: float
    apr_vip: float
    stake_begin_time: datetime
    stake_end_time: datetime


class Launchpool(Base):
    return_coin: str
    desc: str
    total_pool_amount: float
    stake_begin_time: datetime
    stake_end_time: datetime
    stake_pool_list: list[StakePool]
