"""
Database Models for Reality Recording and Memory System
Uses SQLModel for ORM + Pydantic validation
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlmodel import SQLModel, Field, Column, JSON


class RecordType(str, Enum):
    """Types of reality records."""
    BEHAVIOR = "behavior"
    DECISION = "decision"
    EXECUTION = "execution"
    ERROR = "error"


class MemoryType(str, Enum):
    """Types of memory."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class RelationType(str, Enum):
    """Types of memory relationships."""
    RELATED = "related"
    CAUSAL = "causal"
    SIMILAR = "similar"
    CONTRADICTS = "contradicts"


class RealityRecord(SQLModel, table=True):
    """
    Table for recording AI behavior, decisions, and execution results.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    agent_name: str
    agent_type: str  # e.g., "chat", "task", "research"
    action: str
    input_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    confidence_score: Optional[float] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    record_type: RecordType = RecordType.BEHAVIOR
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectState(SQLModel, table=True):
    """
    Table for recording project state changes and milestones.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    state_name: str  # e.g., "planning", "development", "testing", "deployment"
    previous_state: Optional[str] = None
    current_state: str
    description: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ShortTermMemory(SQLModel, table=True):
    """
    Table for short-term memories (session-scoped, time-limited).
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    content: str
    session_id: str
    importance: float = 0.5
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)


class LongTermMemory(SQLModel, table=True):
    """
    Table for long-term memories (persistent, with vector embeddings).
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    content: str
    embedding_id: Optional[str] = None  # Reference to vector store
    importance: float = 0.5
    access_count: int = 0
    summary: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryRelation(SQLModel, table=True):
    """
    Table for tracking relationships between memories.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    source_memory_id: str
    target_memory_id: str
    relation_type: RelationType = RelationType.RELATED
    weight: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
