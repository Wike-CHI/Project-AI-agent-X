"""
Pydantic Models for API Request/Response
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# User Models
class UserBase(BaseModel):
    """Base user model."""
    email: str
    username: str


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserResponse(UserBase):
    """User response model."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Models
class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None


# Message Models
class Message(BaseModel):
    """Chat message model."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    conversation_id: str
    agent_used: Optional[str] = None


# Agent Models
class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    description: str
    role: str
    capabilities: List[str]


class AgentCreate(BaseModel):
    """Agent creation model."""
    name: str
    description: str
    role: str
    goal: str
    backstory: str
    llm_provider: Optional[str] = None
    tools: List[str] = []


# Task Models
class TaskRequest(BaseModel):
    """Task request model."""
    description: str
    expected_output: Optional[str] = None
    agents: List[str] = []
    context: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    status: str
    result: Optional[str] = None
    agent_output: Optional[dict] = None


# Memory Models
class MemoryCreate(BaseModel):
    """Memory creation model."""
    content: str
    memory_type: str  # "episodic", "semantic", "procedural"
    importance: float = 0.5
    metadata: Optional[dict] = None


class MemoryResponse(BaseModel):
    """Memory response model."""
    id: str
    content: str
    memory_type: str
    importance: float
    created_at: datetime
    embedding_id: Optional[str] = None


class MemorySearchRequest(BaseModel):
    """Memory search request model."""
    query: str
    top_k: int = 5
    memory_type: Optional[str] = None


class MemorySearchResponse(BaseModel):
    """Memory search response model."""
    results: List[dict]
