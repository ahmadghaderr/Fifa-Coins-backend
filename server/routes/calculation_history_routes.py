from fastapi import APIRouter, Depends

from server.utils.auth import get_current_user_id
from server.controllers.calculation_history_controller import (
    get_user_calculation_history,
    get_user_total_profit,
    delete_calculation,
    mark_calculation_as_paid
)

router = APIRouter()

@router.get("/calculation-history")
async def calculation_history(user_id: str = Depends(get_current_user_id)):
    return await get_user_calculation_history(user_id)

@router.get("/calculation-history/total")
async def total_profit(user_id: str = Depends(get_current_user_id)):
    return await get_user_total_profit(user_id)

@router.delete("/delete-calculation/{calculation_id}")
async def delete_user_calculation(calculation_id: str, user_id: str = Depends(get_current_user_id)):
    return await delete_calculation(calculation_id, user_id)

@router.patch("/mark-paid/{calculation_id}")
async def mark_paid(calculation_id: str, user_id: str = Depends(get_current_user_id)):
    return await mark_calculation_as_paid(calculation_id, user_id)
