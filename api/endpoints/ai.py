from fastapi import APIRouter, Depends, HTTPException
from api.models.ai import MessageRequest, MessageResponse
from dependencies import get_ai_service
from services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/send_message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        print(f"Processing AI request from user: {request.user_id}")

        parts = await ai_service.get_ai_response(
            request.user_id,
            request.message,
            request.active_todos,
            request.completed_todos
        )

        print(f"AI response generated: {len(parts)} parts")
        return MessageResponse(parts=parts)

    except Exception as e:
        print(f"Error in AI endpoint: {e}")
        return MessageResponse(parts=[
            "Извините, сервис временно недоступен. Попробуйте обратиться позже."
        ])

@router.get("/response_history/{user_id}")
async def get_response_history(
    user_id: str,
    ai_service: AIService = Depends(get_ai_service)
):
    return ai_service.user_conversations.get(user_id, [])