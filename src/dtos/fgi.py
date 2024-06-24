__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from .base import Base


class Fgi(Base):
    timestamp: int
    value: float
    value_classification: str
