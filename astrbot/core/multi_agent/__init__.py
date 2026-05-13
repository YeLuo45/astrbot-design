"""
Multi-Agent Collaboration System

A framework for multi-agent collaboration in AstrBot.
Supports task decomposition, parallel execution, and result aggregation.

Usage:
    from astrbot.core.multi_agent import CodeReviewTeam
    
    team = CodeReviewTeam()
    await team.start()
    result = await team.execute("Review my code")
    await team.stop()
"""

from .agents import (
    BaseAgent,
    CoordinatorAgent,
    CriticAgent,
    SpecialistAgent,
)
from .config import (
    AgentConfig,
    MultiAgentConfig,
    create_default_config,
    get_default_code_review_team,
    get_default_debate_team,
    get_default_research_team,
)
from .context_pool import ContextPool, TaskNode
from .exceptions import (
    AgentExecutionError,
    AgentNotFoundError,
    ContextPoolError,
    CyclicDependencyError,
    InvalidMessageError,
    MessageDeliveryError,
    MultiAgentError,
    TaskNotFoundError,
    TaskTimeoutError,
)
from .message_queue import AgentMessage, MessageBus, MessageType
from .teams import CodeReviewTeam, DebateTeam, ResearchTeam

__all__ = [
    # Core
    "MultiAgentError",
    "TaskTimeoutError",
    "AgentNotFoundError",
    "MessageDeliveryError",
    "TaskNotFoundError",
    "CyclicDependencyError",
    "AgentExecutionError",
    "ContextPoolError",
    "InvalidMessageError",
    # Config
    "MultiAgentConfig",
    "AgentConfig",
    "create_default_config",
    "get_default_code_review_team",
    "get_default_research_team",
    "get_default_debate_team",
    # Message Queue
    "MessageBus",
    "AgentMessage",
    "MessageType",
    # Context Pool
    "ContextPool",
    "TaskNode",
    # Agents
    "BaseAgent",
    "CoordinatorAgent",
    "SpecialistAgent",
    "CriticAgent",
    # Teams
    "CodeReviewTeam",
    "ResearchTeam",
    "DebateTeam",
]
