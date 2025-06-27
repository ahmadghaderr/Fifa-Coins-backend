from ..models.user_model import SignupData
from ..utils.auth import hash_password, verify_password, create_token, decode_token
from ..database import users_collection

from bson import ObjectId
from fastapi import HTTPException
from jose import JWTError

# User signup
async def handle_signup(user: SignupData):
    existing_user = await users_collection.find_one({
        "$or": [{"email": user.email}, {"username": user.username}]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already taken.")

    hashed_pw = hash_password(user.password)

    new_user = {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "hashed_password": hashed_pw
    }

    result = await users_collection.insert_one(new_user)
    user_id = str(result.inserted_id)

    token = create_token({
        "sub": new_user["username"],
        "role": new_user["role"],
        "user_id": user_id
    })

    return {
        "message": "User signed up!",
        "user_id": user_id,
        "access_token": token
    }

# Login handler
async def handle_login(login_data):
    user = await users_collection.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token_data = {
        "sub": user["username"],
        "role": user["role"],
        "user_id": str(user["_id"])
    }
    token = create_token(token_data)
    return {
        "access_token": token,
        "user_id": token_data["user_id"]
    }

# Get user by ID
async def get_user_by_id(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = await users_collection.find_one({"_id": obj_id})
    if user:
        token_data = {
            "sub": user["username"],
            "role": user["role"],
            "user_id": str(user["_id"])
        }
        token = create_token(token_data)

        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "role": user["role"],
            "access_token": token
        }

    raise HTTPException(status_code=404, detail="User not found.")

# Get all users (admin only)
async def get_all_users(token: str):
    try:
        payload = decode_token(token)
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    users_cursor = users_collection.find({})
    users = []
    async for user in users_cursor:
        users.append({
            "id": str(user["_id"]),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "phone": user.get("phone", None),
            "role": user.get("role", "")
        })
    return users

# Delete user by ID (admin only)
async def delete_user_by_id(user_id: str, token: str):
    try:
        payload = decode_token(token)
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    delete_result = await users_collection.delete_one({"_id": obj_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")

    return True
