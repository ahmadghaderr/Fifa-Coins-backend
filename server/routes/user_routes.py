from fastapi import APIRouter, HTTPException, Header

from controllers.user_controller import (
    handle_signup,
    get_user_by_id,
    get_all_users,
    delete_user_by_id
)
from models.user_model import SignupData

router = APIRouter()

@router.post("/signup")
async def signup(user: SignupData):
    try:
        return await handle_signup(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/{id}")
async def get_user(id: str):
    user = await get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/all")
async def read_all_users(token: str):  
    try:
        users = await get_all_users(token)
        return {"users": users}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}",
        )

@router.delete("/delete/{id}")
async def delete_user(id: str, token: str):
    try:
        await delete_user_by_id(id, token)
        return {"message": "User {id} deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

