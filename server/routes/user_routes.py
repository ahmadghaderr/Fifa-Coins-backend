from fastapi import APIRouter, HTTPException, Header

from server.controllers.user_controller import (
    handle_signup,
    handle_login,
    get_user_by_id,
    get_all_users,
    delete_user_by_id,
    edit_user_by_id
)

from server.models.user_model import SignupData, UpdateUserData, LoginData

router = APIRouter()

@router.post("/signup")
async def signup(user: SignupData):
    try:
        return await handle_signup(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(data: LoginData):
    try:
        return await handle_login(data)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

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

@router.put("/edit/{id}")
async def edit_user(id: str, update_data: UpdateUserData):
    try:
        result = await edit_user_by_id(id, update_data)
        return result
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
        return {"message": f"User {id} deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




