from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    market: str
    side: str
    price: float
    size: float
    ts: datetime
