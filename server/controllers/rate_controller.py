from fastapi import HTTPException
from bson import ObjectId

from server.database import database, get_current_rate, set_current_rate

async def get_rate_controller():
    rate = await get_current_rate()
    if rate is None:
        return {"error": "Rate not found"}
    return {"rate": rate}

async def update_rate_controller(new_rate: int, user_id: str):
    try:
        user = await database["users"].find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update the rate")

    if new_rate <= 0:
        return {"error": "Rate must be positive"}

    await set_current_rate(new_rate)
    return {"message": "Rate updated successfully", "rate": new_rate}
