# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Companion - A personal AI companion application powered by multi-agent architecture. The system uses CrewAI for multi-agent collaboration, LlamaIndex for RAG (Retrieval-Augmented Generation), and supports multiple LLM providers (OpenAI, Anthropic Claude, Alibaba Qwen).

## Common Commands

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Copy environment variables
copy .env.example .env

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v
pytest tests/test_api.py -v --no-header  # Run specific test file
pytest tests/ -k "test_chat" -v  # Run tests matching pattern

# Linting and formatting
black . --check
ruff check .
mypy .
```

### Frontend (React + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Linting
npm run lint
```

## Architecture

### Backend Structure (FastAPI)

```
backend/app/
├── api/              # API route handlers
│   ├── routes.py     # Main router that includes sub-routers
│   ├── auth.py       # Authentication endpoints
│   ├── agents.py     # Agent management
│   ├── chat.py       # Chat with AI companion
│   ├── memory.py     # Memory storage/retrieval
│   └── tasks.py      # Task execution
├── agents/           # AI Agent implementations
│   └── base_agent.py # BaseAgent class and AgentRegistry
├── crews/            # CrewAI team configurations
│   └── base_crew.py  # BaseCrew class, CrewStatus enum
├── memory/           # Memory storage layer
├── rag/              # RAG (Retrieval-Augmented Generation)
├── core/             # Configuration and security
│   ├── config.py     # Pydantic Settings (loads from .env)
│   └── security.py   # JWT authentication
├── schemas/          # Pydantic models for API requests/responses
├── services/         # Business logic services
├── main.py           # FastAPI application entry point
```

### Key Design Patterns

**Agent System**: Agents extend `BaseAgent` (abstract class) and are registered via `AgentRegistry`. Configuration uses `AgentConfig` dataclass with role, goal, backstory, and tools.

**Crews**: Teams of agents defined using `BaseCrew`. Tasks are configured via `TaskConfig` dataclass. Execution returns `CrewResult` with status, output, and duration.

**Memory Types**: Three memory types - `episodic` (events), `semantic` (facts), `procedural` (skills). Memory models defined in `schemas/pydantic_models.py`.

**LLM Integration**: Multi-provider support via `settings.DEFAULT_LLM_PROVIDER`. Configured in `.env` with provider-specific API keys and model names.

### API Endpoints

All routes are prefixed with `/api/v1`:
- `POST /auth/register` - User registration
- `POST /auth/login` - JWT token generation
- `POST /chat/` - Chat with AI companion
- `POST /chat/stream` - Streaming chat response
- `GET /agents/` - List available agents
- `POST /memory/` - Create memory
- `GET /memory/` - List/search memories
- `POST /tasks/` - Execute task with crew

## Configuration

Environment variables are loaded via `pydantic-settings` in `app/core/config.py`. Key settings:
- `DEFAULT_LLM_PROVIDER` - LLM provider choice (openai, anthropic, qwen)
- `QDRANT_ENABLED` / `NEO4J_ENABLED` - Enable optional databases
- `DATABASE_URL` - SQLite by default (aiosqlite)

## Database

- Default: SQLite with `aiosqlite` for async operations
- Optional: Qdrant (vector storage for semantic memory), Neo4j (graph storage for episodic memory)
- Models defined in `app/models/database.py` using SQLModel

## Testing

Tests use pytest with FastAPI's `TestClient`. Key test classes in `tests/test_api.py`:
- `TestHealthEndpoints` - Health check tests
- `TestAuthEndpoints` - Authentication tests
- `TestChatEndpoints` - Chat functionality tests
- `TestMemoryEndpoints` - Memory CRUD tests
- `TestAgentEndpoints` - Agent listing tests
- `TestTaskEndpoints` - Task execution tests
