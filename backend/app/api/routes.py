"""
API Routes
"""
from fastapi import APIRouter

from app.api import auth, agents, chat, memory, tasks, record

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(agents.router, prefix="/agents", tags=["Agents"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(memory.router, prefix="/memory", tags=["Memory"])
router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
router.include_router(record.router, prefix="/record", tags=["Record"])
