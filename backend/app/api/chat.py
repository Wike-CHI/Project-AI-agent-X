"""
Chat Routes
"""
import uuid
from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI companion.
    """
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # TODO: Implement actual chat logic with CrewAI/Agno
    # For now, return a mock response
    response = ChatResponse(
        response=f"Echo: {request.message}",
        conversation_id=conversation_id,
        agent_used="default"
    )

    return response


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat with streaming response.
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # TODO: Implement streaming with CrewAI/Agno
    return {
        "conversation_id": conversation_id,
        "message": f"Echo (stream): {request.message}"
    }
