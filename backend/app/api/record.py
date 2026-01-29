"""
API Routes for Reality Recording and Memory Management
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.record_models import RecordType, MemoryType, RelationType
from app.schemas.record_schemas import (
    BehaviorRecordRequest,
    BehaviorRecordResponse,
    StateRecordRequest,
    StateRecordResponse,
    RecordStatsResponse,
    ShortTermMemoryCreate,
    ShortTermMemoryResponse,
    LongTermMemoryCreate,
    LongTermMemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryRelationCreate,
    MemoryRelationResponse,
    MemoryDeleteResponse
)
from app.record.reality_recorder import RealityRecorder, get_recorder
from app.record.memory_service import ProjectMemory, LongTermMemory, get_project_memory, get_long_term_memory


router = APIRouter()
memory_router = APIRouter()

# Global instances (in production, use dependency injection)
_recorder: Optional[RealityRecorder] = None
_project_memory: Optional[ProjectMemory] = None
_long_term_memory: Optional[LongTermMemory] = None


def get_recorder_dep() -> RealityRecorder:
    """Get or create RealityRecorder instance."""
    global _recorder
    if _recorder is None:
        _recorder = RealityRecorder()
    return _recorder


def get_project_memory_dep() -> ProjectMemory:
    """Get or create ProjectMemory instance."""
    global _project_memory
    if _project_memory is None:
        _project_memory = ProjectMemory()
    return _project_memory


def get_long_term_memory_dep() -> LongTermMemory:
    """Get or create LongTermMemory instance."""
    global _long_term_memory
    if _long_term_memory is None:
        _long_term_memory = LongTermMemory()
    return _long_term_memory


# ============== Record Endpoints ==============

@router.post("/behavior", response_model=BehaviorRecordResponse)
async def record_behavior(
    request: BehaviorRecordRequest,
    recorder: RealityRecorder = Depends(get_recorder_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Record an AI behavior, decision, or execution result.
    """
    record = await recorder.record_behavior(
        agent_name=request.agent_name,
        agent_type=request.agent_type,
        action=request.action,
        record_type=request.record_type,
        input_data=request.input_data,
        output_data=request.output_data,
        confidence_score=request.confidence_score,
        duration_ms=request.duration_ms,
        error_message=request.error_message,
        metadata=request.metadata,
        session=db
    )

    return BehaviorRecordResponse(
        id=record.id,
        agent_name=record.agent_name,
        agent_type=record.agent_type,
        action=record.action,
        confidence_score=record.confidence_score,
        duration_ms=record.duration_ms,
        record_type=record.record_type,
        created_at=record.created_at
    )


@router.post("/state", response_model=StateRecordResponse)
async def record_state(
    request: StateRecordRequest,
    recorder: RealityRecorder = Depends(get_recorder_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a project state change.
    """
    state = await recorder.record_state(
        state_name=request.state_name,
        current_state=request.current_state,
        previous_state=request.previous_state,
        description=request.description,
        metadata=request.metadata,
        session=db
    )

    return StateRecordResponse(
        id=state.id,
        state_name=state.state_name,
        previous_state=state.previous_state,
        current_state=state.current_state,
        description=state.description,
        created_at=state.created_at
    )


@router.get("/states", response_model=List[StateRecordResponse])
async def get_state_history(
    state_name: Optional[str] = None,
    limit: int = 100,
    recorder: RealityRecorder = Depends(get_recorder_dep)
):
    """
    Get project state history.
    """
    states = await recorder.get_state_history(state_name=state_name, limit=limit)

    return [
        StateRecordResponse(
            id=state.id,
            state_name=state.state_name,
            previous_state=state.previous_state,
            current_state=state.current_state,
            description=state.description,
            created_at=state.created_at
        )
        for state in states
    ]


@router.get("/stats", response_model=RecordStatsResponse)
async def get_record_stats(
    recorder: RealityRecorder = Depends(get_recorder_dep)
):
    """
    Get statistics about recorded data.
    """
    stats = await recorder.get_stats()

    return RecordStatsResponse(**stats)


# ============== Memory Endpoints ==============

@memory_router.post("/short", response_model=ShortTermMemoryResponse)
async def create_short_term_memory(
    request: ShortTermMemoryCreate,
    memory: ProjectMemory = Depends(get_project_memory_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a short-term memory (session-scoped, time-limited).
    """
    mem = await memory.add_short_term(
        content=request.content,
        session_id=request.session_id,
        importance=request.importance,
        expires_in_seconds=request.expires_in_seconds,
        metadata=request.metadata,
        session=db
    )

    return ShortTermMemoryResponse(
        id=mem.id,
        content=mem.content,
        session_id=mem.session_id,
        memory_type="short_term",
        importance=mem.importance,
        expires_at=mem.expires_at,
        created_at=mem.created_at
    )


@memory_router.get("/short", response_model=List[ShortTermMemoryResponse])
async def get_short_term_memories(
    session_id: str,
    include_expired: bool = False,
    memory: ProjectMemory = Depends(get_project_memory_dep)
):
    """
    Get short-term memories for a session.
    """
    memories = await memory.get_short_term(
        session_id=session_id,
        include_expired=include_expired
    )

    return [
        ShortTermMemoryResponse(
            id=mem.id,
            content=mem.content,
            session_id=mem.session_id,
            memory_type="short_term",
            importance=mem.importance,
            expires_at=mem.expires_at,
            created_at=mem.created_at
        )
        for mem in memories
    ]


@memory_router.post("/long", response_model=LongTermMemoryResponse)
async def create_long_term_memory(
    request: LongTermMemoryCreate,
    memory: LongTermMemory = Depends(get_long_term_memory_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a long-term memory (persistent, with semantic search).
    """
    mem = await memory.add(
        content=request.content,
        importance=request.importance,
        metadata=request.metadata,
        session=db
    )

    return LongTermMemoryResponse(
        id=mem.id,
        content=mem.content,
        memory_type="long_term",
        importance=mem.importance,
        access_count=mem.access_count,
        summary=mem.summary,
        created_at=mem.created_at,
        last_accessed_at=mem.last_accessed_at
    )


@memory_router.post("/long/search", response_model=MemorySearchResponse)
async def search_long_term_memories(
    request: MemorySearchRequest,
    memory: LongTermMemory = Depends(get_long_term_memory_dep)
):
    """
    Search long-term memories by semantic similarity.
    """
    results = await memory.search(
        query=request.query,
        top_k=request.top_k,
        min_importance=request.min_importance,
        memory_type=request.memory_type
    )

    return MemorySearchResponse(
        results=results,
        total_count=len(results)
    )


@memory_router.get("/long", response_model=List[LongTermMemoryResponse])
async def get_long_term_memories(
    limit: int = 100,
    offset: int = 0,
    memory: LongTermMemory = Depends(get_long_term_memory_dep)
):
    """
    Get all long-term memories.
    """
    memories = await memory.get_all(limit=limit, offset=offset)

    return [
        LongTermMemoryResponse(
            id=mem.id,
            content=mem.content,
            memory_type="long_term",
            importance=mem.importance,
            access_count=mem.access_count,
            summary=mem.summary,
            created_at=mem.created_at,
            last_accessed_at=mem.last_accessed_at
        )
        for mem in memories
    ]


@memory_router.delete("/{memory_id}", response_model=MemoryDeleteResponse)
async def delete_memory(
    memory_id: str,
    memory_type: str = "long",
    project_mem: ProjectMemory = Depends(get_project_memory_dep),
    long_mem: LongTermMemory = Depends(get_long_term_memory_dep)
):
    """
    Delete a memory (short-term or long-term).
    """
    if memory_type == "short":
        success = await project_mem.delete_short_term(memory_id)
    else:
        success = await long_mem.delete(memory_id)

    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")

    return MemoryDeleteResponse(id=memory_id)


@memory_router.post("/link", response_model=MemoryRelationResponse)
async def link_memories(
    request: MemoryRelationCreate,
    memory: LongTermMemory = Depends(get_long_term_memory_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a relationship between two memories.
    """
    relation = await memory.link_memories(
        source_id=request.source_memory_id,
        target_id=request.target_memory_id,
        relation_type=request.relation_type,
        weight=request.weight,
        session=db
    )

    return MemoryRelationResponse(
        id=relation.id,
        source_memory_id=relation.source_memory_id,
        target_memory_id=relation.target_memory_id,
        relation_type=relation.relation_type,
        created_at=relation.created_at
    )


# Register memory routes under /memory prefix
router.include_router(memory_router, prefix="/memory")
