"""
Debate Team - Coordinator + Specialist + Critic

Team composition:
- Coordinator: Task decomposition and scheduling
- ProArguer: Argues the pro side
- ConArguer: Argues the con side
- DebateJudge: Judges the debate and provides verdict
"""

from typing import Any, Dict, List, Optional

from ..agents import CoordinatorAgent, CriticAgent, SpecialistAgent
from ..context_pool import ContextPool
from ..message_queue import AgentMessage, MessageBus, MessageType


class ProArguerAgent(SpecialistAgent):
    """Specialist agent that argues the pro side"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute pro argument task"""
        task_description = task.get("task", "")

        # Simulated pro arguments
        arguments = {
            "side": "pro",
            "thesis": f"Supporting: {task_description}",
            "points": [
                "First strong argument in favor",
                "Second supporting point with evidence",
                "Third compelling reason to agree",
            ],
            "conclusion": "The evidence strongly supports this position.",
        }

        return arguments


class ConArguerAgent(SpecialistAgent):
    """Specialist agent that argues the con side"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute con argument task"""
        task_description = task.get("task", "")

        # Simulated con arguments
        arguments = {
            "side": "con",
            "thesis": f"Opposing: {task_description}",
            "points": [
                "First argument against the position",
                "Second counterpoint with concerns",
                "Third objection based on evidence",
            ],
            "conclusion": "The concerns outweigh the proposed benefits.",
        }

        return arguments


class DebateJudgeAgent(CriticAgent):
    """Critic agent that judges the debate"""

    async def evaluate(self, task: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Evaluate debate arguments"""

        if isinstance(result, dict):
            side = result.get("side", "unknown")
            points = result.get("points", [])

            # Judge based on argument quality
            score = min(1.0, len(points) * 0.3 + 0.4)  # More points = higher score

            return {
                "task_id": task.get("task_id"),
                "side": side,
                "scores": [score],
                "overall_score": score,
                "passed": score >= 0.5,
                "feedback": f"{side.title()} arguments scored {score:.2f}",
            }

        return {
            "task_id": task.get("task_id"),
            "scores": [0.5],
            "overall_score": 0.5,
            "passed": True,
            "feedback": "Could not evaluate arguments",
        }


class DebateJudgeFinal(CriticAgent):
    """Final judge that synthesizes both sides"""

    async def evaluate(self, task: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Evaluate final debate results and provide verdict"""
        # This is called with aggregated results from both arguers
        verdict = {
            "verdict": "inconclusive",
            "winning_side": None,
            "summary": "Both sides presented valid arguments",
            "reasoning": "The debate did not produce a clear winner",
        }

        if isinstance(result, dict):
            pro_score = result.get("pro_score", 0.5)
            con_score = result.get("con_score", 0.5)

            if pro_score > con_score + 0.1:
                verdict = {
                    "verdict": "pro",
                    "winning_side": "pro",
                    "summary": "Pro arguments were more compelling",
                    "reasoning": f"Pro scored {pro_score:.2f} vs Con {con_score:.2f}",
                }
            elif con_score > pro_score + 0.1:
                verdict = {
                    "verdict": "con",
                    "winning_side": "con",
                    "summary": "Con arguments were more compelling",
                    "reasoning": f"Con scored {con_score:.2f} vs Pro {pro_score:.2f}",
                }

        return {
            "task_id": task.get("task_id"),
            "scores": [verdict.get("overall_score", 0.5)],
            "overall_score": 0.5,
            "passed": True,
            "feedback": verdict.get("summary", ""),
            "verdict": verdict,
        }


class DebateTeam:
    """
    Pre-configured team for debate workflows.

    Usage:
        team = DebateTeam()
        await team.start()
        result = await team.execute("Should AI be regulated?")
        await team.stop()
    """

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        context_pool: Optional[ContextPool] = None,
    ):
        """
        Initialize the debate team.

        Args:
            message_bus: Optional shared message bus (creates new if None)
            context_pool: Optional shared context pool (creates new if None)
        """
        self.message_bus = message_bus or MessageBus()
        self.context_pool = context_pool or ContextPool()

        # Create agents
        self.coordinator = CoordinatorAgent(
            agent_id="coordinator",
            name="DebateCoordinator",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.pro_arguer = ProArguerAgent(
            agent_id="pro-arguer",
            name="ProArguer",
            domain="pro-argument",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.con_arguer = ConArguerAgent(
            agent_id="con-arguer",
            name="ConArguer",
            domain="con-argument",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.debate_judge = DebateJudgeAgent(
            agent_id="debate-judge",
            name="DebateJudge",
            domain="debate-judgment",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.agents = [
            self.coordinator,
            self.pro_arguer,
            self.con_arguer,
            self.debate_judge,
        ]

    async def start(self) -> None:
        """Start all agents"""
        for agent in self.agents:
            await agent.start()

    async def stop(self) -> None:
        """Stop all agents"""
        for agent in self.agents:
            await agent.stop()

    async def execute(self, topic: str) -> Dict[str, Any]:
        """
        Execute a debate on the given topic.

        Args:
            topic: The debate topic/question

        Returns:
            Dictionary with results from all agents
        """
        from ..context_pool import TaskNode

        root_task = TaskNode(
            type="task",
            status="pending",
            metadata={"description": topic, "team": "debate"},
        )
        await self.context_pool.add_task(root_task)

        message = AgentMessage(
            sender="external",
            recipient="coordinator",
            type=MessageType.TASK,
            payload={
                "task": topic,
                "task_id": root_task.id,
            },
        )
        await self.message_bus.publish(message)

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

        max_wait = 60
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
            "team": "debate",
            "agents": [agent.get_status() for agent in self.agents],
        }
