from models.calculation_model import CalculationInput
from models.calculation_history_model import HistoryEntry
from database import get_current_rate, database
from fastapi import HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

async def calculate_profit(data: CalculationInput, user_id: str):
    rate = await get_current_rate()
    if rate is None:
        raise HTTPException(status_code=500, detail="Current rate not found")

    amount_received = data.buy_price * 0.95  
    coin_profit = amount_received - data.real_price              
    money_profit = (coin_profit * rate) / 1000000

    history_entry = HistoryEntry(
        player_name=data.player_name,
        real_price=data.real_price,
        buy_price=data.buy_price,
        after_tax_received=round(amount_received, 2),
        coin_profit=round(coin_profit, 2),
        rate=rate, 
        money_profit=round(money_profit, 2),
        date=datetime.now(ZoneInfo("Asia/Beirut"))
    )

    await database["calculation_history"].insert_one({
        **history_entry.dict(),
        "user_id": user_id
    })

    return {
        **history_entry.dict(),
        "rate": rate
    }
