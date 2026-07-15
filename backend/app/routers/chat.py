from fastapi import APIRouter

from app.chat_service import answer_question
from app.models import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = answer_question(request.message, request.source_filter)
    return ChatResponse(**result)
