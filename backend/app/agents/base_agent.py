"""
Base Agent Class - Foundation for AI Agents
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    role: str
    goal: str
    backstory: str
    llm_provider: str = settings.DEFAULT_LLM_PROVIDER
    model: str = None
    tools: List[str] = field(default_factory=list)
    verbose: bool = True
    allow_delegation: bool = False


class BaseAgent(ABC):
    """
    Base class for all AI agents in the system.

    Provides common functionality:
    - Configuration management
    - LLM integration
    - Tool management
    - Memory integration
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.role = config.role
        self._memory = None

    @abstractmethod
    async def execute(self, task: str, context: Dict = None) -> Any:
        """
        Execute a task.

        Args:
            task: The task description
            context: Additional context for the task

        Returns:
            Task result
        """
        pass

    @abstractmethod
    async def think(self, input_text: str) -> str:
        """
        Process input and generate response.

        Args:
            input_text: User input

        Returns:
            Generated response
        """
        pass

    def set_memory(self, memory_system):
        """Set the memory system for this agent."""
        self._memory = memory_system

    async def remember(self, key: str, value: str):
        """Store a memory."""
        if self._memory:
            await self._memory.store(key, value)

    async def recall(self, key: str) -> Optional[str]:
        """Recall a memory."""
        if self._memory:
            return await self._memory.recall(key)
        return None

    def __repr__(self):
        return f"<Agent: {self.name} ({self.role})>"


class AgentRegistry:
    """
    Registry for managing agents.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent."""
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())

    def remove(self, name: str):
        """Remove an agent from the registry."""
        if name in self._agents:
            del self._agents[name]


# Global agent registry
agent_registry = AgentRegistry()
