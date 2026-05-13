"""
Research Team - Coordinator + Specialist + Critic

Team composition:
- Coordinator: Task decomposition and scheduling
- WebSearcher: Searches the web for information
- DocAnalyzer: Analyzes documents for key insights
- Synthesizer: Synthesizes findings from multiple sources
"""

from typing import Any, Dict, List, Optional

from ..agents import CoordinatorAgent, CriticAgent, SpecialistAgent
from ..context_pool import ContextPool
from ..message_queue import AgentMessage, MessageBus, MessageType


class WebSearcherAgent(SpecialistAgent):
    """Specialist agent that searches the web"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute web search task"""
        task_description = task.get("task", "")

        # Simulated web search results
        results = {
            "query": task_description,
            "sources": [
                {"title": "Example Source 1", "url": "https://example.com/1", "snippet": "Relevant information..."},
                {"title": "Example Source 2", "url": "https://example.com/2", "snippet": "More information..."},
            ],
            "count": 2,
        }

        return results


class DocAnalyzerAgent(SpecialistAgent):
    """Specialist agent that analyzes documents"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute document analysis task"""
        task_description = task.get("task", "")

        # Simulated document analysis
        analysis = {
            "key_points": [
                "First key insight about the topic",
                "Second important finding",
                "Third conclusion from analysis",
            ],
            "summary": f"Analysis of: {task_description}",
            "confidence": 0.85,
        }

        return analysis


class SynthesizerAgent(SpecialistAgent):
    """Specialist agent that synthesizes information"""

    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute synthesis task"""
        task_description = task.get("task", "")

        # Simulated synthesis
        synthesis = {
            "conclusion": f"Based on research about {task_description}: "
                        "The analysis reveals important insights that suggest "
                        "further investigation may be beneficial.",
            "findings": [
                "Finding 1 from web search",
                "Finding 2 from document analysis",
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
            ],
        }

        return synthesis


class ResearchTeam:
    """
    Pre-configured team for research workflows.

    Usage:
        team = ResearchTeam()
        await team.start()
        result = await team.execute("Research quantum computing applications")
        await team.stop()
    """

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        context_pool: Optional[ContextPool] = None,
    ):
        """
        Initialize the research team.

        Args:
            message_bus: Optional shared message bus (creates new if None)
            context_pool: Optional shared context pool (creates new if None)
        """
        self.message_bus = message_bus or MessageBus()
        self.context_pool = context_pool or ContextPool()

        # Create agents
        self.coordinator = CoordinatorAgent(
            agent_id="coordinator",
            name="ResearchCoordinator",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.web_searcher = WebSearcherAgent(
            agent_id="web-searcher",
            name="WebSearcher",
            domain="web-search",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.doc_analyzer = DocAnalyzerAgent(
            agent_id="doc-analyzer",
            name="DocAnalyzer",
            domain="document-analysis",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.synthesizer = SynthesizerAgent(
            agent_id="synthesizer",
            name="Synthesizer",
            domain="synthesis",
            message_bus=self.message_bus,
            context_pool=self.context_pool,
        )

        self.agents = [
            self.coordinator,
            self.web_searcher,
            self.doc_analyzer,
            self.synthesizer,
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
        Execute a research task.

        Args:
            task: Task description

        Returns:
            Dictionary with results from all agents
        """
        from ..context_pool import TaskNode

        root_task = TaskNode(
            type="task",
            status="pending",
            metadata={"description": task, "team": "research"},
        )
        await self.context_pool.add_task(root_task)

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
            "team": "research",
            "agents": [agent.get_status() for agent in self.agents],
        }
