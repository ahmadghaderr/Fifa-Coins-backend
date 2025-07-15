from fastapi import APIRouter
from pydantic import BaseModel
from server.controllers.chatbot_controller import handle_chatbot_message

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/chatbot")
async def chatbot_endpoint(data: ChatMessage):
    reply = await handle_chatbot_message(data.message)
    return {"reply": reply}
