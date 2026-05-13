"""
Multi-Agent API Integration

Provides REST API endpoints for multi-agent operations.
"""

import asyncio
import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException

from astrbot.core.multi_agent import (
    CodeReviewTeam,
    ContextPool,
    DebateTeam,
    MessageBus,
    ResearchTeam,
    TaskNode,
)

router = APIRouter(prefix="/api/multi-agent", tags=["multi-agent"])

# Global state for active teams and tasks
_active_teams: Dict[str, Any] = {}
_task_contexts: Dict[str, Dict[str, Any]] = {}


def _get_team(team_type: str) -> Any:
    """Get or create a team instance"""
    if team_type not in _active_teams:
        if team_type == "code-review":
            _active_teams[team_type] = CodeReviewTeam()
        elif team_type == "research":
            _active_teams[team_type] = ResearchTeam()
        elif team_type == "debate":
            _active_teams[team_type] = DebateTeam()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown team type: {team_type}")
    return _active_teams[team_type]


@router.post("/execute")
async def execute_task(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a multi-agent task.

    Request body:
        team: Team type ("code-review", "research", "debate")
        task: Task description

    Returns:
        task_id: Unique identifier for the task
        status: "started"
    """
    team_type = request.get("team", "code-review")
    task = request.get("task", "")

    if not task:
        raise HTTPException(status_code=400, detail="Task description is required")

    # Validate team type
    valid_teams = ["code-review", "research", "debate"]
    if team_type not in valid_teams:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid team type. Must be one of: {valid_teams}"
        )

    # Create task context
    task_id = str(uuid.uuid4())
    message_bus = MessageBus()
    context_pool = ContextPool()

    _task_contexts[task_id] = {
        "team_type": team_type,
        "task": task,
        "status": "running",
        "message_bus": message_bus,
        "context_pool": context_pool,
    }

    # Start team and execute
    try:
        if team_type == "code-review":
            team = CodeReviewTeam(message_bus=message_bus, context_pool=context_pool)
        elif team_type == "research":
            team = ResearchTeam(message_bus=message_bus, context_pool=context_pool)
        elif team_type == "debate":
            team = DebateTeam(message_bus=message_bus, context_pool=context_pool)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown team: {team_type}")

        _active_teams[task_id] = team
        await team.start()

        # Execute in background
        asyncio.create_task(_execute_and_store(task_id, team, task))

        return {
            "task_id": task_id,
            "status": "started",
            "team": team_type,
            "message": "Task is being processed",
        }

    except Exception as e:
        _task_contexts[task_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_and_store(task_id: str, team: Any, task: str):
    """Execute task and store result"""
    try:
        result = await team.execute(task)
        _task_contexts[task_id]["result"] = result
        _task_contexts[task_id]["status"] = "done"
    except Exception as e:
        _task_contexts[task_id]["error"] = str(e)
        _task_contexts[task_id]["status"] = "failed"
    finally:
        await team.stop()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a task.

    Returns:
        task_id: Task identifier
        status: Current status
        team: Team type
    """
    if task_id not in _task_contexts:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    context = _task_contexts[task_id]
    return {
        "task_id": task_id,
        "status": context.get("status", "unknown"),
        "team": context.get("team_type", "unknown"),
        "task": context.get("task", ""),
    }


@router.get("/result/{task_id}")
async def get_task_result(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a completed task.

    Returns:
        task_id: Task identifier
        result: Task result
        status: Task status
    """
    if task_id not in _task_contexts:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    context = _task_contexts[task_id]
    status = context.get("status", "unknown")

    if status == "running":
        return {
            "task_id": task_id,
            "status": "running",
            "message": "Task is still running",
        }
    elif status == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": context.get("error", "Unknown error"),
        }
    elif status == "done":
        return {
            "task_id": task_id,
            "status": "done",
            "result": context.get("result", {}),
        }
    else:
        return {
            "task_id": task_id,
            "status": status,
        }


@router.get("/memory/{task_id}")
async def get_context_snapshot(task_id: str) -> Dict[str, Any]:
    """
    Get a snapshot of the context pool for a task.

    Returns:
        task_id: Task identifier
        snapshot: Context pool snapshot
    """
    if task_id not in _task_contexts:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    context = _task_contexts[task_id]
    context_pool = context.get("context_pool")

    if context_pool is None:
        raise HTTPException(status_code=404, detail="Context pool not available")

    snapshot = await context_pool.snapshot()
    return {
        "task_id": task_id,
        "snapshot": snapshot,
    }


@router.get("/teams")
async def list_teams() -> Dict[str, Any]:
    """
    List available team types.

    Returns:
        teams: List of available team configurations
    """
    return {
        "teams": [
            {
                "id": "code-review",
                "name": "Code Review Team",
                "description": "Code generation, review, and quality critique",
                "agents": ["coordinator", "code-generator", "code-reviewer", "code-critic"],
            },
            {
                "id": "research",
                "name": "Research Team",
                "description": "Web search, document analysis, and synthesis",
                "agents": ["coordinator", "web-searcher", "doc-analyzer", "synthesizer"],
            },
            {
                "id": "debate",
                "name": "Debate Team",
                "description": "Pro/con arguments with judge",
                "agents": ["coordinator", "pro-arguer", "con-arguer", "debate-judge"],
            },
        ]
    }


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a running task.

    Returns:
        task_id: Task identifier
        status: "cancelled"
    """
    if task_id not in _task_contexts:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    context = _task_contexts[task_id]
    context["status"] = "cancelled"

    # Stop the team if running
    if task_id in _active_teams:
        await _active_teams[task_id].stop()
        del _active_teams[task_id]

    return {
        "task_id": task_id,
        "status": "cancelled",
    }
