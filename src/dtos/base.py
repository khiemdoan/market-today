__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

pattern = re.compile(r'(?<!^)(?=[A-Z])')


class Base(BaseModel):
    def __init__(self, **data: dict[str, Any]) -> None:
        new_data = {}
        for key, value in data.items():
            new_key = pattern.sub('_', key).lower()
            new_data[new_key] = value
        super().__init__(**new_data)

        for k, v in self.__dict__.items():
            if isinstance(v, datetime):
                setattr(self, k, v.replace(tzinfo=timezone.utc))
            if isinstance(v, Decimal):
                setattr(self, k, v.normalize())
