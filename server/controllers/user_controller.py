from server.models.user_model import SignupData
from server.utils.auth import hash_password, verify_password, create_token, decode_token
from server.database import users_collection

from bson import ObjectId
from fastapi import HTTPException
from jose import JWTError

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


async def handle_login(login_data: LoginData):
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
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "access_token": token
    }
    

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
async def edit_user_by_id(user_id: str, update_data: UpdateUserData):
    update_fields = {}

    if update_data.username:
        update_fields["username"] = update_data.username

    if update_data.email:
        update_fields["email"] = update_data.email

    if update_data.password:
        update_fields["hashed_password"] = hash_password(update_data.password)

    if update_data.phone:
        update_fields["phone"] = update_data.phone

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update.")

    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    if "email" in update_fields:
        existing_email = await users_collection.find_one({
            "email": update_fields["email"],
            "_id": {"$ne": obj_id}
        })
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already in use.")

    if "username" in update_fields:
        existing_username = await users_collection.find_one({
            "username": update_fields["username"],
            "_id": {"$ne": obj_id}
        })
        if existing_username:
            raise HTTPException(status_code=400, detail="Username is already in use.")

    result = await users_collection.update_one(
        {"_id": obj_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"message": "User information updated successfully."}    

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

    return {"message": "User deleted successfully."}
