"""
Chat Routes - Integrated with behavior recording and memory system
"""
import uuid
from fastapi import APIRouter, Depends

from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, get_chat_service, create_chat_service

router = APIRouter()


def get_chat_service_dep() -> ChatService:
    """Get the chat service instance."""
    return get_chat_service()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service_dep)
):
    """
    Chat with the AI companion.

    This endpoint integrates with:
    - Reality Recording: Records all chat behaviors and decisions
    - Memory System: Stores conversation context in short-term memory
    - LLM Service: Generates responses using configured provider
    """
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    try:
        result = await chat_service.chat(
            message=request.message,
            conversation_id=conversation_id,
            context=request.context
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            agent_used=result["agent_used"]
        )
    except Exception as e:
        # Return error response
        return ChatResponse(
            response=f"Error: {str(e)}",
            conversation_id=conversation_id,
            agent_used="error"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service_dep)
):
    """
    Chat with streaming response.

    Streaming is not yet implemented - returns basic response.
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # TODO: Implement streaming with CrewAI/Agno
    result = await chat_service.chat(
        message=request.message,
        conversation_id=conversation_id,
        context=request.context
    )

    return {
        "conversation_id": result["conversation_id"],
        "message": result["response"],
        "agent_used": result["agent_used"]
    }


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 10,
    chat_service: ChatService = Depends(get_chat_service_dep)
):
    """
    Get conversation history from memory.

    Args:
        conversation_id: Conversation identifier
        limit: Maximum number of messages to retrieve
    """
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        limit=limit
    )
    return {"conversation_id": conversation_id, "history": history}


@router.post("/search")
async def search_memories(
    query: str,
    top_k: int = 5,
    chat_service: ChatService = Depends(get_chat_service_dep)
):
    """
    Search long-term memories for relevant information.

    Args:
        query: Search query
        top_k: Maximum results
    """
    results = await chat_service.search_memories(query=query, top_k=top_k)
    return {"query": query, "results": results}
