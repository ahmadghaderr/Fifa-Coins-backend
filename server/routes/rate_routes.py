from fastapi import APIRouter, HTTPException, Depends

from server.controllers.rate_controller import get_rate_controller, update_rate_controller
from server.utils.auth import get_current_user_id

router = APIRouter()

@router.get("/rate")
async def get_rate():
    result = await get_rate_controller()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.put("/update-rate")
async def update_rate(rate: int, user_id: str = Depends(get_current_user_id)):
    result = await update_rate_controller(rate, user_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
