from fastapi import APIRouter, HTTPException

from server.models.user_model import LoginData
from server.controllers.user_controller import handle_login

router = APIRouter()

@router.post("/login")
async def login(user: LoginData):
    try:
        return await handle_login(user)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
