"""
CrewAI Integration - Multi-Agent Collaboration
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.agents.base_agent import BaseAgent, AgentConfig, agent_registry


class CrewStatus(str, Enum):
    """Status of a crew execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskConfig:
    """Configuration for a task."""
    description: str
    expected_output: str = None
    agent: str = None  # Agent name to execute
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CrewResult:
    """Result of a crew execution."""
    status: CrewStatus
    output: str = None
    tasks_output: Dict[str, Any] = field(default_factory=dict)
    error: str = None
    duration_seconds: float = 0.0


class BaseCrew:
    """
    CrewAI integration for multi-agent collaboration.

    Features:
    - Define agent teams with specific roles
    - Sequential or parallel task execution
    - Context sharing between agents
    - Result aggregation
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        agents: List[BaseAgent] = None,
        verbose: bool = True
    ):
        self.name = name
        self.description = description
        self.agents = agents or []
        self.verbose = verbose

        # Register agents
        for agent in self.agents:
            agent_registry.register(agent)

    def add_agent(self, agent: BaseAgent):
        """Add an agent to the crew."""
        self.agents.append(agent)
        agent_registry.register(agent)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return agent_registry.get(name)

    async def execute(
        self,
        tasks: List[TaskConfig],
        context: Dict = None
    ) -> CrewResult:
        """
        Execute tasks with the crew.

        Args:
            tasks: List of tasks to execute
            context: Shared context for all tasks

        Returns:
            CrewResult with outputs
        """
        import time
        start_time = time.time()

        result = CrewResult(status=CrewStatus.RUNNING)
        context = context or {}
        tasks_output = {}

        try:
            # Execute tasks (sequentially for now)
            for task_config in tasks:
                # Get the agent for this task
                agent_name = task_config.agent or self.agents[0].name if self.agents else None
                agent = self.get_agent(agent_name) if agent_name else None

                if agent:
                    # Execute task with agent
                    task_output = await agent.execute(
                        task_config.description,
                        context={**context, **tasks_output}
                    )
                    tasks_output[task_config.description] = task_output
                else:
                    # No agent available, use mock execution
                    tasks_output[task_config.description] = f"Completed: {task_config.description}"

            result.status = CrewStatus.COMPLETED
            result.output = self._aggregate_outputs(tasks_output)
            result.tasks_output = tasks_output

        except Exception as e:
            result.status = CrewStatus.FAILED
            result.error = str(e)

        result.duration_seconds = time.time() - start_time
        return result

    def _aggregate_outputs(self, outputs: Dict[str, Any]) -> str:
        """Aggregate task outputs into a summary."""
        # TODO: Implement proper output aggregation
        return "\n\n".join([
            f"=== {task} ===\n{output}"
            for task, output in outputs.items()
        ])

    def __repr__(self):
        return f"<Crew: {self.name} ({len(self.agents)} agents)>"


# Pre-defined crew configurations
class ChatCrew(BaseCrew):
    """Crew for conversational interactions."""

    def __init__(self):
        super().__init__(
            name="ChatCrew",
            description="Handles user conversations"
        )
        # Add chat-specific agents here


class ResearchCrew(BaseCrew):
    """Crew for research and information gathering."""

    def __init__(self):
        super().__init__(
            name="ResearchCrew",
            description="Conducts research on topics"
        )


class MemoryCrew(BaseCrew):
    """Crew for memory management operations."""

    def __init__(self):
        super().__init__(
            name="MemoryCrew",
            description="Manages memory storage and retrieval"
        )
