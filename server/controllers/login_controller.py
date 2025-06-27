from fastapi import HTTPException
from models.user_model import LoginData
from database import users_collection
from utils.auth import verify_password, create_token

async def handle_login(login_data: LoginData):
    user = await users_collection.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_token({
        "sub": user["username"],    
        "role": user["role"],
        "user_id": str(user["_id"])
    })

    return {
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "access_token": token
    }
