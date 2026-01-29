"""
Pydantic Schemas for Record and Memory API Requests/Responses
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.record_models import RecordType, MemoryType, RelationType


# ============== Record Schemas ==============

class BehaviorRecordRequest(BaseModel):
    """Request schema for recording AI behavior."""
    agent_name: str = Field(..., description="Name of the agent")
    agent_type: str = Field(..., description="Type of agent (e.g., chat, task)")
    action: str = Field(..., description="Action performed")
    input_data: Optional[Dict[str, Any]] = Field(default=None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(default=None, description="Output data")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score")
    duration_ms: Optional[float] = Field(default=None, ge=0, description="Execution duration in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    record_type: RecordType = Field(default=RecordType.BEHAVIOR, description="Type of record")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class BehaviorRecordResponse(BaseModel):
    """Response schema for behavior record."""
    id: str
    agent_name: str
    agent_type: str
    action: str
    confidence_score: Optional[float] = None
    duration_ms: Optional[float] = None
    record_type: RecordType
    created_at: datetime

    class Config:
        from_attributes = True


class StateRecordRequest(BaseModel):
    """Request schema for recording project state."""
    state_name: str = Field(..., description="Name of the state")
    previous_state: Optional[str] = Field(default=None, description="Previous state")
    current_state: str = Field(..., description="Current state")
    description: Optional[str] = Field(default=None, description="State description")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class StateRecordResponse(BaseModel):
    """Response schema for state record."""
    id: str
    state_name: str
    previous_state: Optional[str] = None
    current_state: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecordStatsResponse(BaseModel):
    """Response schema for record statistics."""
    total_records: int
    by_agent_type: Dict[str, int]
    by_record_type: Dict[str, int]
    success_rate: float
    avg_duration_ms: float


# ============== Memory Schemas ==============

class ShortTermMemoryCreate(BaseModel):
    """Request schema for creating short-term memory."""
    content: str = Field(..., description="Memory content")
    session_id: str = Field(..., description="Session identifier")
    importance: float = Field(default=0.5, ge=0, le=1, description="Importance score")
    expires_in_seconds: int = Field(default=3600, ge=60, description="Expiration time in seconds")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ShortTermMemoryResponse(BaseModel):
    """Response schema for short-term memory."""
    id: str
    content: str
    session_id: str
    memory_type: str = "short_term"
    importance: float
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class LongTermMemoryCreate(BaseModel):
    """Request schema for creating long-term memory."""
    content: str = Field(..., description="Memory content")
    importance: float = Field(default=0.5, ge=0, le=1, description="Importance score")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class LongTermMemoryResponse(BaseModel):
    """Response schema for long-term memory."""
    id: str
    content: str
    memory_type: str = "long_term"
    importance: float
    access_count: int
    summary: Optional[str] = None
    created_at: datetime
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    """Request schema for searching memories."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Maximum results")
    memory_type: Optional[MemoryType] = Field(default=None, description="Filter by memory type")
    min_importance: Optional[float] = Field(default=None, ge=0, le=1, description="Minimum importance filter")


class MemoryCreateRequest(BaseModel):
    """Request schema for creating a memory (short or long term)."""
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    session_id: Optional[str] = Field(default=None, description="Session ID for short-term memory")
    importance: float = Field(default=0.5, ge=0, le=1, description="Importance score")
    expires_in_seconds: Optional[int] = Field(default=None, ge=60, description="Expiration time for short-term memory")


class MemorySearchResult(BaseModel):
    """Single memory search result."""
    id: str
    content: str
    memory_type: str
    importance: float
    score: float
    created_at: datetime


class MemorySearchResponse(BaseModel):
    """Response schema for memory search."""
    results: List[MemorySearchResult]
    total_count: int


class MemoryRelationCreate(BaseModel):
    """Request schema for creating memory relationship."""
    source_memory_id: str
    target_memory_id: str
    relation_type: RelationType = RelationType.RELATED
    weight: float = Field(default=1.0, ge=0, le=1)


class MemoryRelationResponse(BaseModel):
    """Response schema for memory relationship."""
    id: str
    source_memory_id: str
    target_memory_id: str
    relation_type: RelationType
    created_at: datetime

    class Config:
        from_attributes = True


class MemoryDeleteResponse(BaseModel):
    """Response schema for memory deletion."""
    id: str
    message: str = "Memory deleted successfully"
