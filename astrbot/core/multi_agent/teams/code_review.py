"""
Code Review Team - Coordinator + Specialist + Critic

Team composition:
- Coordinator: Task decomposition and scheduling
- CodeGenerator: Generates code implementations
- CodeReviewer: Reviews code for issues
- CodeCritic: Evaluates code quality
"""

from typing import Any, Dict, List, Optional

from ..agents import CoordinatorAgent, CriticAgent, SpecialistAgent
from ..context_pool import ContextPool
from ..message_queue import AgentMessage, MessageBus, MessageType


class CodeGeneratorAgent(SpecialistAgent):
    """Specialist agent that generates code"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute code generation task"""
        task_description = task.get("task", "")

        # Simulated code generation
        code = f"# Generated code for: {task_description}\n"
        code += "def implementation():\n"
        code += "    pass  # TODO: Implement\n"

        return {
            "type": "code",
            "language": "python",
            "code": code,
            "description": task_description,
        }


class CodeReviewerAgent(SpecialistAgent):
    """Specialist agent that reviews code"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute code review task"""
        task_description = task.get("task", "")

        # Simulated code review
        review = {
            "issues": [
                {"severity": "warning", "line": 2, "message": "Missing docstring"},
                {"severity": "info", "line": 3, "message": "Consider using type hints"},
            ],
            "score": 7.5,
            "summary": f"Code review for: {task_description}",
        }

        return review


class CodeCriticAgent(CriticAgent):
    """Critic agent that evaluates code quality"""

    async def evaluate(self, task: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Evaluate code quality"""
        if isinstance(result, dict):
            score = result.get("score", 0.5)
            issues = result.get("issues", [])

            # Quality based on score and issue count
            quality_score = score / 10.0
            if len(issues) > 3:
                quality_score *= 0.7
            elif len(issues) > 0:
                quality_score *= 0.9

            return {
                "task_id": task.get("task_id"),
                "scores": [quality_score],
                "overall_score": quality_score,
                "passed": quality_score >= 0.6,
                "feedback": f"Code quality: {quality_score:.2f}, Issues: {len(issues)}",
            }

        return {
            "task_id": task.get("task_id"),
            "scores": [0.5],
            "overall_score": 0.5,
            "passed": False,
            "feedback": "Could not evaluate result",
        }


class CodeReviewTeam:
    """
    Pre-configured team for code review workflows.

    Usage:
        team = CodeReviewTeam()
        await team.start()
        result = await team.execute("Review this code: def foo(): pass")
        await team.stop()
    """

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        context_pool: Optional[ContextPool] = None,
    ):
        """
        Initialize the code review team.

        Args:
            message_bus: Optional shared message bus (creates new if None)
            context_pool: Optional shared context pool (creates new if None)
        """
        self.message_bus = message_bus or MessageBus()
        self.context_pool = context_pool or ContextPool()

        # Create agents
        self.coordinator = CoordinatorAgent(
            agent_id="coordinator",
            name="CodeReviewCoordinator",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.code_generator = CodeGeneratorAgent(
            agent_id="code-generator",
            name="CodeGenerator",
            domain="code",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.code_reviewer = CodeReviewerAgent(
            agent_id="code-reviewer",
            name="CodeReviewer",
            domain="code-review",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.code_critic = CodeCriticAgent(
            agent_id="code-critic",
            name="CodeCritic",
            domain="code-quality",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.agents = [
            self.coordinator,
            self.code_generator,
            self.code_reviewer,
            self.code_critic,
        ]

    async def start(self) -> None:
        """Start all agents"""
        for agent in self.agents:
            await agent.start()

    async def stop(self) -> None:
        """Stop all agents"""
        for agent in self.agents:
            await agent.stop()

    async def execute(self, task: str) -> Dict[str, Any]:
        """
        Execute a code review task.

        Args:
            task: Task description

        Returns:
            Dictionary with results from all agents
        """
        # Create a root task
        from ..context_pool import TaskNode

        root_task = TaskNode(
            type="task",
            status="pending",
            metadata={"description": task, "team": "code-review"},
        )
        await self.context_pool.add_task(root_task)

        # Send task to coordinator
        message = AgentMessage(
            sender="external",
            recipient="coordinator",
            type=MessageType.TASK,
            payload={
                "task": task,
                "task_id": root_task.id,
            },
        )
        await self.message_bus.publish(message)

        # Wait for completion (simplified - in production use proper await)
        import asyncio

        try:
            result = await asyncio.wait_for(
                self._wait_for_result(root_task.id), timeout=60.0
            )
            return result
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "task_id": root_task.id,
                "message": "Task timed out",
            }

    async def _wait_for_result(self, task_id: str) -> Dict[str, Any]:
        """Wait for task result"""
        import asyncio

        max_wait = 60  # seconds
        waited = 0
        poll_interval = 0.5

        while waited < max_wait:
            result = await self.context_pool.get(f"result:{task_id}")
            if result:
                return result

            task = await self.context_pool.get_task(task_id)
            if task and task.status == "done":
                return await self.context_pool.get(f"result:{task_id}")

            await asyncio.sleep(poll_interval)
            waited += poll_interval

        raise asyncio.TimeoutError()

    def get_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "team": "code-review",
            "agents": [agent.get_status() for agent in self.agents],
        }
