from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
database = client.fifacoins

users_collection = database.get_collection("users")
rates_collection = database.get_collection("rates")

async def get_current_rate():
    rate_doc = await rates_collection.find_one({"_id": "current_rate"})
    if rate_doc:
        return rate_doc["rate"]
    return None  

# Set or update current rate in DB
async def set_current_rate(new_rate: int):
    await rates_collection.update_one(
        {"_id": "current_rate"},
        {"$set": {"rate": new_rate}},
        upsert=True
    )
