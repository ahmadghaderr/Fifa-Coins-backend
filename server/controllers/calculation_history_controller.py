from fastapi import HTTPException
from bson import ObjectId

from ..database import database

async def get_user_calculation_history(user_id: str):
    history = await database["calculation_history"].find({"user_id": user_id}).to_list(1000)
    for entry in history:
        entry["_id"] = str(entry["_id"])  
    return history

async def get_user_total_profit(user_id: str):
    history = await database["calculation_history"].find({"user_id": user_id}).to_list(1000)

    total_coin_profit = sum(float(h.get("buy_price", 0) or 0) for h in history)
    total_money_profit = sum(float(h.get("money_profit", 0) or 0) for h in history)

    total_paid_money_profit = sum(
        float(h.get("money_profit", 0) or 0)
        for h in history
        if h.get("is_paid") == True
    )

    return {
        "total_profit_coins": round(total_coin_profit, 2),
        "total_profit_money": round(total_money_profit, 2),
        "total_paid_money_profit": round(total_paid_money_profit, 2)
    }

async def delete_calculation(calculation_id: str, user_id: str):
    record = await database["calculation_history"].find_one({"_id": ObjectId(calculation_id)})
    if not record:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if record["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    player_name = record.get("player_name", "Unknown Player")
    await database["calculation_history"].delete_one({"_id": ObjectId(calculation_id)})

    return {"message": f"Calculation for player '{player_name}' deleted successfully"}

async def mark_calculation_as_paid(calculation_id: str, user_id: str):
    record = await database["calculation_history"].find_one({"_id": ObjectId(calculation_id)})
    if not record:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if record["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await database["calculation_history"].update_one(
        {"_id": ObjectId(calculation_id)},
        {"$set": {"is_paid": True}}
    )
    return {"message": "Marked as paid"}
