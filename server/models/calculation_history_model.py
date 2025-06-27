from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import pytz

lebanon_tz = pytz.timezone("Asia/Beirut")

def leb_now():
    return datetime.now(lebanon_tz)

class HistoryEntry(BaseModel):
    player_name: str
    real_price: float
    buy_price: float
    after_tax_received: float
    coin_profit: float
    money_profit: float
    rate: float
    date: Optional[datetime] = Field(default_factory=leb_now)
    is_paid: bool = False
