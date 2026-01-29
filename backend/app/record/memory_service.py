"""
Memory Service - Manages short-term and long-term memories
Includes auto-summary mechanism and background cleanup tasks
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.record_models import (
    ShortTermMemory as ShortTermMemoryModel,
    LongTermMemory as LongTermMemoryModel,
    MemoryRelation as MemoryRelationModel,
    MemoryType,
    RelationType
)
from app.rag.vector_store import VectorStore, get_vector_store
from app.services.llm_service import LLMService, get_llm_service


class ProjectMemory:
    """
    Service for managing short-term memories (session-scoped).
    """

    def __init__(self):
        """Initialize the project memory service."""
        self._memory_cache: Dict[str, ShortTermMemoryModel] = {}

    async def add_short_term(
        self,
        content: str,
        session_id: str,
        importance: float = 0.5,
        expires_in_seconds: int = 3600,
        extra_data: Optional[Dict[str, Any]] = None,
        session: AsyncSession = None
    ) -> ShortTermMemoryModel:
        """
        Add a short-term memory.

        Args:
            content: Memory content
            session_id: Session identifier
            importance: Importance score (0-1)
            expires_in_seconds: Expiration time in seconds
            extra_data: Additional metadata
            session: Database session (optional)

        Returns:
            ShortTermMemoryModel instance
        """
        memory = ShortTermMemoryModel(
            id=str(uuid4()),
            content=content,
            session_id=session_id,
            importance=importance,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in_seconds),
            extra_data=extra_data,
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow()
        )

        # Store in cache for quick access
        self._memory_cache[memory.id] = memory

        # In production, save to database
        # if session:
        #     session.add(memory)
        #     await session.commit()

        return memory

    async def get_short_term(
        self,
        session_id: str,
        include_expired: bool = False
    ) -> List[ShortTermMemoryModel]:
        """
        Get short-term memories for a session.

        Args:
            session_id: Session identifier
            include_expired: Include expired memories

        Returns:
            List of ShortTermMemoryModel instances
        """
        now = datetime.utcnow()
        memories = []

        for memory in self._memory_cache.values():
            if memory.session_id != session_id:
                continue
            if not include_expired and memory.expires_at < now:
                continue
            memories.append(memory)

        # Sort by importance (descending) and creation time (descending)
        memories.sort(key=lambda m: (-m.importance, m.created_at))

        return memories

    async def delete_short_term(
        self,
        memory_id: str,
        session: AsyncSession = None
    ) -> bool:
        """
        Delete a short-term memory.

        Args:
            memory_id: Memory ID to delete
            session: Database session (optional)

        Returns:
            True if deleted, False if not found
        """
        if memory_id in self._memory_cache:
            del self._memory_cache[memory_id]
            return True
        return False

    async def cleanup_expired(self) -> int:
        """
        Remove all expired short-term memories.

        Returns:
            Number of memories deleted
        """
        now = datetime.utcnow()
        expired_ids = [
            mem_id for mem_id, memory in self._memory_cache.items()
            if memory.expires_at < now
        ]

        for mem_id in expired_ids:
            del self._memory_cache[mem_id]

        return len(expired_ids)


class MemorySummarizer:
    """
    Service for auto-summarizing memories using LLM.
    """

    def __init__(self, llm_service: LLMService = None):
        """
        Initialize the memory summarizer.

        Args:
            llm_service: LLM service for generating summaries
        """
        self._llm_service = llm_service or get_llm_service()
        self._summary_cache: Dict[str, str] = {}

    async def summarize_memories(
        self,
        memories: List[str],
        context: str = ""
    ) -> str:
        """
        Generate a summary from multiple memory contents.

        Args:
            memories: List of memory contents to summarize
            context: Additional context for summarization

        Returns:
            Generated summary string
        """
        if not memories:
            return ""

        # Build prompt for summarization
        memory_texts = "\n".join(f"- {mem}" for mem in memories[:20])  # Limit to 20 memories
        prompt = f"""请对以下记忆内容进行总结，提取关键信息和模式：

{context}
记忆内容：
{memory_texts}

请用简洁的中文总结这些记忆的核心要点，保留最重要的信息（100字以内）。"""

        try:
            summary = await self._llm_service.complete(prompt)
            return summary.strip()
        except Exception:
            # Fallback: return concatenated first memory
            return memories[0][:100] if memories else ""

    async def extract_key_points(
        self,
        content: str,
        max_points: int = 3
    ) -> List[str]:
        """
        Extract key points from a single memory content.

        Args:
            content: Memory content to analyze
            max_points: Maximum number of key points to extract

        Returns:
            List of key points
        """
        prompt = f"""请从以下内容中提取关键要点（最多{max_points}个）：

{content}

关键要点（用换行分隔）："""

        try:
            result = await self._llm_service.complete(prompt)
            points = [p.strip() for p in result.split('\n') if p.strip()]
            return points[:max_points]
        except Exception:
            return [content[:100]] if content else []

    async def should_promote_to_long_term(
        self,
        short_term_memories: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Evaluate which short-term memories should be promoted to long-term.

        Args:
            short_term_memories: List of short-term memory data
            threshold: Importance threshold for promotion

        Returns:
            List of memories recommended for promotion
        """
        if not short_term_memories:
            return []

        # Calculate average importance
        avg_importance = sum(m.get('importance', 0) for m in short_term_memories) / len(short_term_memories)

        if avg_importance < threshold:
            return []

        # Get memories with above-threshold importance
        promoted = [
            m for m in short_term_memories
            if m.get('importance', 0) >= threshold
        ]

        return promoted


class MemoryCleanupTask:
    """
    Background task for memory expiration and cleanup.
    """

    def __init__(
        self,
        short_term_service: 'ProjectMemory',
        long_term_service: 'LongTermMemory',
        interval_seconds: int = 300  # 5 minutes
    ):
        """
        Initialize the cleanup task.

        Args:
            short_term_service: Short-term memory service
            long_term_service: Long-term memory service
            interval_seconds: Cleanup interval in seconds
        """
        self._short_term = short_term_service
        self._long_term = long_term_service
        self._interval = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the background cleanup task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_cleanup_loop())

    async def stop(self):
        """Stop the background cleanup task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_cleanup_loop(self):
        """Run the cleanup loop."""
        while self._running:
            try:
                await self.cleanup_all()
            except Exception as e:
                # Log error but continue running
                print(f"Memory cleanup error: {e}")
            await asyncio.sleep(self._interval)

    async def cleanup_all(self) -> Dict[str, int]:
        """
        Perform full cleanup of expired and low-importance memories.

        Returns:
            Dictionary with cleanup counts
        """
        results = {
            "expired_short_term": 0,
            "archived_low_importance": 0,
            "deleted_relations": 0
        }

        # Clean expired short-term memories
        results["expired_short_term"] = await self._short_term.cleanup_expired()

        # Archive low-importance long-term memories
        results["archived_low_importance"] = await self._long_term.cleanup_low_importance()

        return results

    async def cleanup_short_term_only(self) -> int:
        """Clean expired short-term memories only."""
        return await self._short_term.cleanup_expired()

    async def cleanup_long_term_only(
        self,
        threshold: float = 0.1,
        retention_days: int = 30
    ) -> int:
        """Clean low-importance long-term memories only."""
        return await self._long_term.cleanup_low_importance(
            threshold=threshold,
            retention_days=retention_days
        )


class LongTermMemory:
    """
    Service for managing long-term memories (persistent, with vector embeddings).
    """

    def __init__(
        self,
        vector_store: VectorStore = None,
        llm_service: LLMService = None,
        summarizer: MemorySummarizer = None
    ):
        """
        Initialize the long-term memory service.

        Args:
            vector_store: Vector store for semantic search
            llm_service: LLM service for summarization
            summarizer: Memory summarizer instance
        """
        self._memory_cache: Dict[str, LongTermMemoryModel] = {}
        self._vector_store = vector_store or get_vector_store()
        self._llm_service = llm_service or get_llm_service()
        self._summarizer = summarizer or MemorySummarizer(self._llm_service)

    async def add(
        self,
        content: str,
        importance: float = 0.5,
        extra_data: Optional[Dict[str, Any]] = None,
        generate_embedding: bool = True,
        auto_summarize: bool = False,
        session: AsyncSession = None
    ) -> LongTermMemoryModel:
        """
        Add a long-term memory.

        Args:
            content: Memory content
            importance: Importance score (0-1)
            extra_data: Additional metadata
            generate_embedding: Whether to generate vector embedding
            auto_summarize: Whether to auto-generate summary using LLM
            session: Database session (optional)

        Returns:
            LongTermMemoryModel instance
        """
        embedding_id = None
        summary = None

        # Generate embedding if requested
        if generate_embedding:
            ids = await self._vector_store.add_texts([content])
            if ids:
                embedding_id = ids[0]

        # Auto-generate summary if requested
        if auto_summarize:
            try:
                summary = await self._summarizer.extract_key_points(content, max_points=1)
                summary = summary[0] if summary else None
            except Exception:
                summary = None

        memory = LongTermMemoryModel(
            id=str(uuid4()),
            content=content,
            embedding_id=embedding_id,
            importance=importance,
            summary=summary,
            extra_data=extra_data,
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Store in cache
        self._memory_cache[memory.id] = memory

        # In production, save to database
        # if session:
        #     session.add(memory)
        #     await session.commit()

        return memory

    async def add_with_summary(
        self,
        content: str,
        importance: float = 0.5,
        extra_data: Optional[Dict[str, Any]] = None,
        generate_embedding: bool = True,
        session: AsyncSession = None
    ) -> LongTermMemoryModel:
        """
        Add a long-term memory with auto-generated summary.

        Args:
            content: Memory content
            importance: Importance score (0-1)
            extra_data: Additional metadata
            generate_embedding: Whether to generate vector embedding
            session: Database session (optional)

        Returns:
            LongTermMemoryModel instance with summary
        """
        return await self.add(
            content=content,
            importance=importance,
            extra_data=extra_data,
            generate_embedding=generate_embedding,
            auto_summarize=True,
            session=session
        )

    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_importance: Optional[float] = None,
        memory_type: Optional[MemoryType] = None
    ) -> List[Dict[str, Any]]:
        """
        Search long-term memories by semantic similarity.

        Args:
            query: Search query
            top_k: Maximum results
            min_importance: Minimum importance filter
            memory_type: Filter by memory type

        Returns:
            List of search results with content, score, and metadata
        """
        # Vector search
        vector_results = await self._vector_store.search(query, top_k=top_k)

        # Filter and format results
        results = []
        for result in vector_results:
            if result.id in self._memory_cache:
                memory = self._memory_cache[result.id]
                if min_importance is not None and memory.importance < min_importance:
                    continue

                results.append({
                    "id": result.id,
                    "content": result.content,
                    "memory_type": "long_term",
                    "importance": memory.importance,
                    "score": result.score,
                    "created_at": memory.created_at.isoformat()
                })

        return results

    async def get(
        self,
        memory_id: str
    ) -> Optional[LongTermMemoryModel]:
        """
        Get a long-term memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            LongTermMemoryModel instance or None
        """
        memory = self._memory_cache.get(memory_id)
        if memory:
            # Update access count and time
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        return memory

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[LongTermMemoryModel]:
        """
        Get all long-term memories.

        Args:
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of LongTermMemoryModel instances
        """
        memories = list(self._memory_cache.values())
        memories.sort(key=lambda m: (-m.importance, m.created_at))
        return memories[offset:offset + limit]

    async def update_importance(
        self,
        memory_id: str,
        delta: float = 0.1,
        session: AsyncSession = None
    ) -> Optional[LongTermMemoryModel]:
        """
        Update memory importance score.

        Args:
            memory_id: Memory ID
            delta: Change in importance
            session: Database session (optional)

        Returns:
            Updated LongTermMemoryModel or None
        """
        memory = self._memory_cache.get(memory_id)
        if memory:
            memory.importance = min(1.0, max(0.0, memory.importance + delta))
            memory.updated_at = datetime.utcnow()
        return memory

    async def delete(
        self,
        memory_id: str,
        session: AsyncSession = None
    ) -> bool:
        """
        Delete a long-term memory.

        Args:
            memory_id: Memory ID
            session: Database session (optional)

        Returns:
            True if deleted, False if not found
        """
        if memory_id in self._memory_cache:
            # Delete from vector store
            if self._memory_cache[memory_id].embedding_id:
                await self._vector_store.delete([self._memory_cache[memory_id].embedding_id])

            del self._memory_cache[memory_id]
            return True
        return False

    async def link_memories(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType = RelationType.RELATED,
        weight: float = 1.0,
        session: AsyncSession = None
    ) -> MemoryRelationModel:
        """
        Create a relationship between two memories.

        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            relation_type: Type of relationship
            weight: Relationship weight
            session: Database session (optional)

        Returns:
            MemoryRelationModel instance
        """
        relation = MemoryRelationModel(
            id=str(uuid4()),
            source_memory_id=source_id,
            target_memory_id=target_id,
            relation_type=relation_type,
            weight=weight,
            created_at=datetime.utcnow()
        )

        # In production, save to database
        # if session:
        #     session.add(relation)
        #     await session.commit()

        return relation

    async def get_related(
        self,
        memory_id: str,
        relation_type: Optional[RelationType] = None,
        depth: int = 2
    ) -> List[LongTermMemoryModel]:
        """
        Get memories related to a given memory.

        Args:
            memory_id: Source memory ID
            relation_type: Filter by relation type
            depth: How many hops to traverse

        Returns:
            List of related LongTermMemoryModel instances
        """
        # In production, query from database with graph traversal
        return []

    async def cleanup_low_importance(
        self,
        threshold: float = 0.1,
        retention_days: int = 30
    ) -> int:
        """
        Clean up low-importance memories.

        Args:
            threshold: Importance threshold below which to archive
            retention_days: Days to retain before archiving

        Returns:
            Number of memories archived
        """
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=retention_days)

        archived_count = 0
        to_delete = []

        for memory_id, memory in self._memory_cache.items():
            if memory.importance < threshold and memory.created_at < cutoff_date:
                to_delete.append(memory_id)

        for mem_id in to_delete:
            await self.delete(mem_id)
            archived_count += 1

        return archived_count


# Global instances
project_memory = ProjectMemory()
long_term_memory = LongTermMemory()
memory_summarizer = MemorySummarizer()
_cleanup_task: Optional[MemoryCleanupTask] = None


def get_project_memory() -> ProjectMemory:
    """Get the project memory instance."""
    return project_memory


def get_long_term_memory() -> LongTermMemory:
    """Get the long-term memory instance."""
    return long_term_memory


def get_memory_summarizer() -> MemorySummarizer:
    """Get the memory summarizer instance."""
    return memory_summarizer


def get_memory_cleanup_task(
    interval_seconds: int = 300
) -> MemoryCleanupTask:
    """
    Get or create the memory cleanup task instance.

    Args:
        interval_seconds: Cleanup interval in seconds

    Returns:
        MemoryCleanupTask instance
    """
    global _cleanup_task
    if _cleanup_task is None:
        _cleanup_task = MemoryCleanupTask(
            short_term_service=project_memory,
            long_term_service=long_term_memory,
            interval_seconds=interval_seconds
        )
    return _cleanup_task


async def start_memory_cleanup_task(interval_seconds: int = 300):
    """
    Start the background memory cleanup task.

    Args:
        interval_seconds: Cleanup interval in seconds
    """
    task = get_memory_cleanup_task(interval_seconds)
    await task.start()


async def stop_memory_cleanup_task():
    """Stop the background memory cleanup task."""
    global _cleanup_task
    if _cleanup_task is not None:
        await _cleanup_task.stop()
        _cleanup_task = None
