"""
Agent Routes
"""
from fastapi import APIRouter, HTTPException

from app.schemas import AgentResponse, AgentCreate

router = APIRouter()

# Mock agent registry
agents_registry = {}


@router.get("/", response_model=list[AgentResponse])
async def list_agents():
    """List all available agents."""
    return list(agents_registry.values())


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID."""
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )
    return agents_registry[agent_id]


@router.post("/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent."""
    import uuid
    agent_id = str(uuid.uuid4())[:8]

    agent = AgentResponse(
        id=agent_id,
        name=agent_data.name,
        description=agent_data.description,
        role=agent_data.role,
        capabilities=agent_data.tools
    )

    agents_registry[agent_id] = agent
    return agent


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found"
        )

    del agents_registry[agent_id]
    return {"message": f"Agent {agent_id} deleted"}
