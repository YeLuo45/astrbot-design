"""
Multi-Agent Collaboration System - Exceptions
"""

from typing import Optional


class MultiAgentError(Exception):
    """Base exception for multi-agent system"""

    def __init__(self, message: str, agent_id: Optional[str] = None):
        self.message = message
        self.agent_id = agent_id
        super().__init__(self.message)


class TaskTimeoutError(MultiAgentError):
    """Raised when a task exceeds its timeout"""

    def __init__(self, task_id: str, timeout: float):
        self.task_id = task_id
        self.timeout = timeout
        super().__init__(f"Task {task_id} exceeded timeout of {timeout}s")


class AgentNotFoundError(MultiAgentError):
    """Raised when an agent is not found"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        super().__init__(f"Agent not found: {agent_id}")


class MessageDeliveryError(MultiAgentError):
    """Raised when message delivery fails"""

    def __init__(self, message_id: str, recipient: str, reason: str):
        self.message_id = message_id
        self.recipient = recipient
        self.reason = reason
        super().__init__(
            f"Failed to deliver message {message_id} to {recipient}: {reason}"
        )


class TaskNotFoundError(MultiAgentError):
    """Raised when a task is not found"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class CyclicDependencyError(MultiAgentError):
    """Raised when a cyclic dependency is detected"""

    def __init__(self, task_id: str, dependency_chain: list):
        self.task_id = task_id
        self.dependency_chain = dependency_chain
        super().__init__(
            f"Cyclic dependency detected for task {task_id}: {' -> '.join(dependency_chain)}"
        )


class AgentExecutionError(MultiAgentError):
    """Raised when agent execution fails"""

    def __init__(self, agent_id: str, task_id: str, reason: str):
        self.agent_id = agent_id
        self.task_id = task_id
        self.reason = reason
        super().__init__(f"Agent {agent_id} failed to execute task {task_id}: {reason}")


class ContextPoolError(MultiAgentError):
    """Raised when context pool operation fails"""

    pass


class InvalidMessageError(MultiAgentError):
    """Raised when a message is invalid"""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid message: {reason}")
