"""
Memory Routes
"""
import uuid
from fastapi import APIRouter, HTTPException

from app.schemas import (
    MemoryCreate,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse
)

router = APIRouter()

# Mock memory storage
memory_store = {}


@router.post("/", response_model=MemoryResponse)
async def create_memory(memory_data: MemoryCreate):
    """Create a new memory."""
    import datetime

    memory_id = str(uuid.uuid4())
    memory_entry = {
        "id": memory_id,
        "content": memory_data.content,
        "memory_type": memory_data.memory_type,
        "importance": memory_data.importance,
        "metadata": memory_data.metadata,
        "created_at": str(datetime.datetime.utcnow())
    }

    memory_store[memory_id] = memory_entry

    return MemoryResponse(
        id=memory_id,
        content=memory_data.content,
        memory_type=memory_data.memory_type,
        importance=memory_data.importance,
        created_at=memory_entry["created_at"]
    )


@router.get("/", response_model=list[MemoryResponse])
async def list_memories(memory_type: str = None):
    """List all memories, optionally filtered by type."""
    memories = list(memory_store.values())

    if memory_type:
        memories = [m for m in memories if m["memory_type"] == memory_type]

    return [
        MemoryResponse(
            id=m["id"],
            content=m["content"],
            memory_type=m["memory_type"],
            importance=m["importance"],
            created_at=m["created_at"]
        )
        for m in memories
    ]


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(request: MemorySearchRequest):
    """Search memories by semantic similarity."""
    # TODO: Implement actual vector search with Qdrant
    # For now, return mock results
    return MemorySearchResponse(
        results=[
            {
                "id": "mock-1",
                "content": f"Related to: {request.query}",
                "score": 0.95,
                "memory_type": "semantic"
            }
        ]
    )


@router.get("/{memory_id}")
async def get_memory(memory_id: str):
    """Get a specific memory by ID."""
    if memory_id not in memory_store:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory_store[memory_id]


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory."""
    if memory_id not in memory_store:
        raise HTTPException(status_code=404, detail="Memory not found")

    del memory_store[memory_id]
    return {"message": "Memory deleted"}
