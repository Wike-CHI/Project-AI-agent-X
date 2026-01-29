"""
Task Routes
"""
import uuid
from fastapi import APIRouter, HTTPException

from app.schemas import TaskRequest, TaskResponse

router = APIRouter()

# Mock task storage
tasks_store = {}


@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskRequest):
    """Create and execute a task with AI agents."""
    task_id = str(uuid.uuid4())

    task = TaskResponse(
        task_id=task_id,
        status="pending",
        result=None,
        agent_output=None
    )

    tasks_store[task_id] = task

    # TODO: Implement actual task execution with CrewAI
    # For now, set to completed with mock result
    task.status = "completed"
    task.result = f"Task executed: {task_data.description}"

    return task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks():
    """List all tasks."""
    return list(tasks_store.values())


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_store[task_id]


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks_store[task_id]
    return {"message": "Task deleted"}
