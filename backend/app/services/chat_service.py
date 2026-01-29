"""
Chat Service - Integrates with reality recording and memory system
"""
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.llm_service import LLMService, get_llm_service
from app.services.llm_service import LLMProvider  # Re-export for type hints
from app.record.reality_recorder import RealityRecorder, get_recorder
from app.record.memory_service import ProjectMemory, LongTermMemory, get_project_memory, get_long_term_memory
from app.models.record_models import RecordType


class ChatService:
    """
    Chat service with integrated behavior recording and memory.

    Features:
    - LLM-based chat responses
    - Automatic behavior/decision recording
    - Memory integration (short-term and long-term)
    """

    def __init__(
        self,
        llm_service: LLMService = None,
        recorder: RealityRecorder = None,
        project_memory: ProjectMemory = None,
        long_term_memory: LongTermMemory = None,
        agent_name: str = "chat_agent",
        agent_type: str = "chat"
    ):
        """
        Initialize the chat service.

        Args:
            llm_service: LLM service for generating responses
            recorder: Reality recorder for behavior logging
            project_memory: Short-term memory service
            long_term_memory: Long-term memory service
            agent_name: Name of the agent
            agent_type: Type of agent
        """
        self._llm = llm_service or get_llm_service()
        self._recorder = recorder or get_recorder()
        self._project_memory = project_memory or get_project_memory()
        self._long_term_memory = long_term_memory or get_long_term_memory()
        self._agent_name = agent_name
        self._agent_type = agent_type

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        record_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate a response.

        Args:
            message: User message
            conversation_id: Conversation identifier
            context: Conversation history
            record_memory: Whether to record to memory

        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()

        # Build conversation context
        messages = context or []
        messages.append({"role": "user", "content": message})

        try:
            # Generate response using LLM
            response_content = await self._llm.complete(
                prompt=message,
                provider=None  # Use default provider
            )

            duration_ms = (time.time() - start_time) * 1000

            # Record behavior
            if record_memory:
                await self._record_chat_behavior(
                    message=message,
                    response=response_content,
                    duration_ms=duration_ms,
                    conversation_id=conversation_id,
                    success=True
                )

                # Store in short-term memory
                await self._project_memory.add_short_term(
                    content=f"User said: {message}",
                    session_id=conversation_id or "default",
                    importance=0.5,
                    expires_in_seconds=3600
                )

                # Store important responses in long-term memory
                if len(response_content) > 100:
                    await self._long_term_memory.add(
                        content=f"Response to '{message[:50]}...': {response_content[:200]}",
                        importance=0.6
                    )

            return {
                "response": response_content,
                "conversation_id": conversation_id,
                "agent_used": self._agent_name,
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Record error behavior
            if record_memory:
                await self._record_chat_behavior(
                    message=message,
                    response=None,
                    duration_ms=duration_ms,
                    conversation_id=conversation_id,
                    success=False,
                    error_message=str(e)
                )

            raise

    async def _record_chat_behavior(
        self,
        message: str,
        response: Optional[str],
        duration_ms: float,
        conversation_id: Optional[str],
        success: bool,
        error_message: Optional[str] = None
    ):
        """
        Record chat behavior to reality recorder.

        Args:
            message: User message
            response: AI response
            duration_ms: Response time
            conversation_id: Conversation ID
            success: Whether the chat was successful
            error_message: Error message if failed
        """
        await self._recorder.record_behavior(
            agent_name=self._agent_name,
            agent_type=self._agent_type,
            action="chat_response",
            record_type=RecordType.BEHAVIOR,
            input_data={"message": message, "conversation_id": conversation_id},
            output_data={"response": response} if response else None,
            confidence_score=1.0 if success else 0.0,
            duration_ms=duration_ms,
            error_message=error_message
        )

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from short-term memory.

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of memories to retrieve

        Returns:
            List of conversation messages
        """
        memories = await self._project_memory.get_short_term(
            session_id=conversation_id
        )

        # Filter and format memories
        conversations = []
        for mem in memories[:limit]:
            if mem.extra_data and "message" in (mem.extra_data or {}):
                conversations.append({
                    "content": mem.content,
                    "timestamp": mem.created_at.isoformat(),
                    "importance": mem.importance
                })

        return conversations

    async def search_memories(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search long-term memories for relevant information.

        Args:
            query: Search query
            top_k: Maximum results

        Returns:
            List of relevant memories
        """
        return await self._long_term_memory.search(query=query, top_k=top_k)

    async def store_memory(
        self,
        content: str,
        importance: float = 0.5,
        is_long_term: bool = True
    ) -> str:
        """
        Store a memory.

        Args:
            content: Memory content
            importance: Importance score (0-1)
            is_long_term: Whether to store in long-term memory

        Returns:
            Memory ID
        """
        if is_long_term:
            memory = await self._long_term_memory.add(
                content=content,
                importance=importance
            )
            return memory.id
        else:
            memory = await self._project_memory.add_short_term(
                content=content,
                session_id="default",
                importance=importance
            )
            return memory.id


# Global chat service instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def create_chat_service(
    agent_name: str = "chat_agent",
    agent_type: str = "chat"
) -> ChatService:
    """
    Create a new chat service instance.

    Args:
        agent_name: Name of the agent
        agent_type: Type of agent

    Returns:
        ChatService instance
    """
    return ChatService(
        agent_name=agent_name,
        agent_type=agent_type
    )
