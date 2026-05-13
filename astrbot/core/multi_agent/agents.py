"""
Multi-Agent Collaboration System - Agent Base Classes

Implements BaseAgent, CoordinatorAgent, SpecialistAgent, and CriticAgent.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .context_pool import ContextPool
from .exceptions import AgentExecutionError, AgentNotFoundError
from .message_queue import AgentMessage, MessageBus, MessageType


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.

    Each agent has:
    - Unique ID and name
    - Message queue for receiving messages
    - Connection to shared context pool
    - Lifecycle management (start/stop)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        message_bus: MessageBus,
        context_pool: ContextPool,
        topics: Optional[List[str]] = None,
    ):
        """
        Initialize a base agent.

        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name
            message_bus: Shared message bus instance
            context_pool: Shared context pool instance
            topics: List of topics to subscribe to
        """
        self.agent_id = agent_id
        self.name = name
        self.message_bus = message_bus
        self.context_pool = context_pool
        self.topics = topics or [MessageType.TASK.value, MessageType.STOP.value]

        self._running = False
        self._task = None
        self._heartbeat_task = None

    async def start(self) -> None:
        """Start the agent's message processing loop"""
        if self._running:
            return

        self._running = True
        await self.message_bus.subscribe(self.agent_id, self.topics)
        self._task = asyncio.create_task(self._process_messages())
        self._heartbeat_task = asyncio.create_task(self._heartbeat())

    async def stop(self) -> None:
        """Stop the agent"""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

    async def _process_messages(self) -> None:
        """Main message processing loop"""
        while self._running:
            try:
                message = await self.message_bus.get(self.agent_id, timeout=1.0)
                if message:
                    await self.handle_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue processing
                print(f"Agent {self.agent_id} error: {e}")

    async def _heartbeat(self) -> None:
        """Send periodic heartbeat messages"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                if self._running:
                    heartbeat = AgentMessage(
                        sender=self.agent_id,
                        type=MessageType.HEARTBEAT,
                        payload={"agent_id": self.agent_id, "timestamp": datetime.now().isoformat()},
                    )
                    await self.message_bus.publish(heartbeat)
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def send_to(self, recipient: str, message: AgentMessage) -> None:
        """
        Send a message to a specific agent.

        Args:
            recipient: ID of the recipient agent
            message: The message to send
        """
        message.sender = self.agent_id
        message.recipient = recipient
        await self.message_bus.publish(message)

    async def broadcast(self, message: AgentMessage) -> None:
        """
        Broadcast a message to all subscribed agents.

        Args:
            message: The message to broadcast
        """
        message.sender = self.agent_id
        message.recipient = None  # None indicates broadcast
        await self.message_bus.publish(message)

    async def reply_to(self, original: AgentMessage, payload: Dict[str, Any]) -> None:
        """
        Reply to a message.

        Args:
            original: The original message to reply to
            payload: The reply payload
        """
        reply = AgentMessage(
            sender=self.agent_id,
            recipient=original.sender,
            type=MessageType.RESULT,
            payload=payload,
            correlation_id=original.correlation_id,
            reply_to=original.id,
        )
        await self.message_bus.publish(reply)

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> None:
        """
        Handle an incoming message.

        Args:
            message: The incoming message
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of this agent.

        Returns:
            Dictionary with status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "running": self._running,
            "queue_size": self.message_bus.get_queue_size(self.agent_id),
            "topics": self.topics,
        }


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent responsible for:
    - Understanding user intent
    - Decomposing tasks into subtasks
    - Scheduling specialist agents
    - Aggregating final results
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        message_bus: MessageBus,
        context_pool: ContextPool,
    ):
        super().__init__(agent_id, name, message_bus, context_pool)
        self.active_tasks: Dict[str, Dict] = {}

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages"""
        if message.type == MessageType.TASK:
            await self._handle_task(message)
        elif message.type == MessageType.RESULT:
            await self._handle_result(message)
        elif message.type == MessageType.CRITIQUE:
            await self._handle_critique(message)
        elif message.type == MessageType.STOP:
            await self._handle_stop(message)

    async def _handle_task(self, message: AgentMessage) -> None:
        """Process a new task"""
        task_description = message.payload.get("task", "")
        task_id = message.payload.get("task_id", str(uuid.uuid4()))

        # Store task info
        self.active_tasks[task_id] = {
            "description": task_description,
            "status": "decomposing",
            "subtasks": [],
            "results": {},
        }

        # Decompose the task
        subtasks = await self.decompose(task_description)

        # Schedule subtasks
        schedule_result = await self.schedule(subtasks)

        self.active_tasks[task_id]["status"] = "running"
        self.active_tasks[task_id]["subtasks"] = subtasks
        self.active_tasks[task_id]["schedule"] = schedule_result

    async def decompose(self, task: str) -> List[Dict[str, Any]]:
        """
        Decompose a task into subtasks.

        This is a simplified implementation. In production, this could use
        an LLM to intelligently decompose the task.

        Args:
            task: The task description

        Returns:
            List of subtask dictionaries
        """
        # Simple heuristic decomposition
        subtasks = []

        if "code" in task.lower() or "implement" in task.lower():
            subtasks.append({
                "id": f"{task[:8]}-gen",
                "type": "specialist",
                "specialist_type": "code-generator",
                "description": "Generate code",
            })
            subtasks.append({
                "id": f"{task[:8]}-review",
                "type": "specialist",
                "specialist_type": "code-reviewer",
                "description": "Review code",
            })
            subtasks.append({
                "id": f"{task[:8]}-critique",
                "type": "critic",
                "specialist_type": "code-critic",
                "description": "Evaluate code quality",
            })
        elif "research" in task.lower() or "analyze" in task.lower():
            subtasks.append({
                "id": f"{task[:8]}-search",
                "type": "specialist",
                "specialist_type": "web-searcher",
                "description": "Search web",
            })
            subtasks.append({
                "id": f"{task[:8]}-analyze",
                "type": "specialist",
                "specialist_type": "doc-analyzer",
                "description": "Analyze documents",
            })
            subtasks.append({
                "id": f"{task[:8]}-synthesize",
                "type": "specialist",
                "specialist_type": "synthesizer",
                "description": "Synthesize findings",
            })
        elif "debate" in task.lower() or "discuss" in task.lower():
            subtasks.append({
                "id": f"{task[:8]}-pro",
                "type": "specialist",
                "specialist_type": "pro-arguer",
                "description": "Argue pro side",
            })
            subtasks.append({
                "id": f"{task[:8]}-con",
                "type": "specialist",
                "specialist_type": "con-arguer",
                "description": "Argue con side",
            })
            subtasks.append({
                "id": f"{task[:8]}-judge",
                "type": "critic",
                "specialist_type": "debate-judge",
                "description": "Judge debate",
            })
        else:
            # Generic task
            subtasks.append({
                "id": f"{task[:8]}-execute",
                "type": "specialist",
                "specialist_type": "generic",
                "description": task,
            })

        return subtasks

    async def schedule(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Schedule subtasks for execution.

        Args:
            subtasks: List of subtasks to schedule

        Returns:
            Schedule information
        """
        schedule = {
            "total": len(subtasks),
            "parallel_groups": [],
            "assignments": {},
        }

        # Group by parallel execution capability
        # Critics usually run after specialists
        parallel_group = []
        for subtask in subtasks:
            if subtask["type"] == "critic":
                # Finish current group and start new one for critics
                if parallel_group:
                    schedule["parallel_groups"].append(parallel_group)
                parallel_group = [subtask]
            else:
                parallel_group.append(subtask)

        if parallel_group:
            schedule["parallel_groups"].append(parallel_group)

        # Send messages to each agent
        for subtask in subtasks:
            agent_id = subtask.get("specialist_type", "unknown")
            message = AgentMessage(
                sender=self.agent_id,
                recipient=agent_id,
                type=MessageType.TASK,
                payload={
                    "task": subtask["description"],
                    "task_id": subtask["id"],
                    "parent_id": subtask.get("parent_id"),
                },
            )
            await self.message_bus.publish(message)
            schedule["assignments"][subtask["id"]] = agent_id

        return schedule

    async def aggregate(self, results: Dict[str, Any]) -> str:
        """
        Aggregate results from multiple agents.

        Args:
            results: Dictionary of results keyed by task ID

        Returns:
            Aggregated result string
        """
        if not results:
            return "No results to aggregate"

        # Simple aggregation - combine all results
        aggregated = []
        for task_id, result in results.items():
            aggregated.append(f"Task {task_id}: {result}")

        return "\n".join(aggregated)

    async def _handle_result(self, message: AgentMessage) -> None:
        """Handle a result message from a specialist"""
        task_id = message.payload.get("task_id")
        result = message.payload.get("result")

        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id]["results"][message.sender] = result

    async def _handle_critique(self, message: AgentMessage) -> None:
        """Handle a critique message"""
        # Process critique and decide if retry is needed
        critique = message.payload
        task_id = critique.get("task_id")

        if task_id and task_id in self.active_tasks:
            passed = critique.get("passed", False)
            if not passed and critique.get("retry_count", 0) < 3:
                # Request retry
                await self._request_retry(task_id, critique)
            else:
                # Accept result
                await self._accept_result(task_id, critique)

    async def _handle_stop(self, message: AgentMessage) -> None:
        """Handle a stop message"""
        task_id = message.payload.get("task_id")
        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "stopped"

    async def _request_retry(self, task_id: str, critique: Dict) -> None:
        """Request a retry from a specialist"""
        message = AgentMessage(
            sender=self.agent_id,
            type=MessageType.TASK,
            payload={
                "task_id": task_id,
                "retry": True,
                "feedback": critique.get("feedback"),
            },
        )
        # Broadcast to specialists
        await self.broadcast(message)

    async def _accept_result(self, task_id: str, critique: Dict) -> None:
        """Accept a result"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "done"
            self.active_tasks[task_id]["final_critique"] = critique


class SpecialistAgent(BaseAgent):
    """
    Specialist agent that executes domain-specific tasks.

    Subclasses should implement the execute() method with their specific logic.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        domain: str,
        message_bus: MessageBus,
        context_pool: ContextPool,
    ):
        """
        Initialize a specialist agent.

        Args:
            agent_id: Unique identifier
            name: Human-readable name
            domain: Domain area (e.g., "code", "research")
            message_bus: Shared message bus
            context_pool: Shared context pool
        """
        super().__init__(agent_id, name, message_bus, context_pool)
        self.domain = domain
        self._current_tasks: Set[str] = set()

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages"""
        if message.type == MessageType.TASK:
            await self._handle_task(message)
        elif message.type == MessageType.STOP:
            await self._handle_stop(message)

    async def _handle_task(self, message: AgentMessage) -> None:
        """Handle a task assignment"""
        task_id = message.payload.get("task_id", str(uuid.uuid4()))
        task_data = message.payload.get("task", "")

        self._current_tasks.add(task_id)

        try:
            # Update status to running
            await self.context_pool.update_task_status(task_id, "running")

            # Execute the task
            result = await self.execute({
                "task_id": task_id,
                "task": task_data,
                "retry": message.payload.get("retry", False),
                "feedback": message.payload.get("feedback"),
            })

            # Store result
            await self.context_pool.put(f"result:{task_id}", result)

            # Update status to done
            await self.context_pool.update_task_status(task_id, "done", result)

            # Send result back to coordinator
            reply = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                type=MessageType.RESULT,
                payload={
                    "task_id": task_id,
                    "result": result,
                    "agent_id": self.agent_id,
                },
                correlation_id=message.correlation_id,
                reply_to=message.id,
            )
            await self.message_bus.publish(reply)

        except Exception as e:
            # Update status to failed
            await self.context_pool.update_task_status(task_id, "failed", str(e))

            # Send error result
            error_reply = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                type=MessageType.RESULT,
                payload={
                    "task_id": task_id,
                    "error": str(e),
                    "agent_id": self.agent_id,
                },
                correlation_id=message.correlation_id,
                reply_to=message.id,
            )
            await self.message_bus.publish(error_reply)

        finally:
            self._current_tasks.discard(task_id)

    async def _handle_stop(self, message: AgentMessage) -> None:
        """Handle a stop message"""
        task_id = message.payload.get("task_id")
        if task_id in self._current_tasks:
            # Note: In a real implementation, we'd want to gracefully cancel
            self._current_tasks.discard(task_id)

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Any:
        """
        Execute the specialist's domain-specific task.

        Args:
            task: Task dictionary containing task_id, task description, etc.

        Returns:
            The task result
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        base_status = super().get_status()
        base_status.update({
            "domain": self.domain,
            "current_tasks": list(self._current_tasks),
        })
        return base_status


class CriticAgent(BaseAgent):
    """
    Critic agent that evaluates task results and provides quality feedback.

    Used to ensure quality standards are met before accepting results.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        domain: str,
        message_bus: MessageBus,
        context_pool: ContextPool,
        threshold: float = 0.7,
    ):
        """
        Initialize a critic agent.

        Args:
            agent_id: Unique identifier
            name: Human-readable name
            domain: Domain area for evaluation criteria
            message_bus: Shared message bus
            context_pool: Shared context pool
            threshold: Minimum score to pass (0-1)
        """
        super().__init__(agent_id, name, message_bus, context_pool)
        self.domain = domain
        self.threshold = threshold
        self._evaluation_history: Dict[str, List[Dict]] = {}

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages"""
        if message.type == MessageType.RESULT:
            await self._handle_result(message)
        elif message.type == MessageType.TASK:
            await self._handle_task(message)

    async def _handle_result(self, message: AgentMessage) -> None:
        """Evaluate a result from a specialist"""
        task_id = message.payload.get("task_id")
        result = message.payload.get("result")

        if not task_id or result is None:
            return

        # Evaluate the result
        evaluation = await self.evaluate(
            {"task_id": task_id, "result": result},
            result
        )

        # Track evaluation history
        if task_id not in self._evaluation_history:
            self._evaluation_history[task_id] = []
        self._evaluation_history[task_id].append(evaluation)

        # Send critique back
        critique_message = AgentMessage(
            sender=self.agent_id,
            recipient=message.sender,
            type=MessageType.CRITIQUE,
            payload={
                "task_id": task_id,
                "scores": evaluation.get("scores", []),
                "passed": evaluation.get("passed", False),
                "feedback": evaluation.get("feedback", ""),
                "retry_count": len(self._evaluation_history[task_id]),
            },
            correlation_id=message.correlation_id,
            reply_to=message.id,
        )
        await self.message_bus.publish(critique_message)

    async def _handle_task(self, message: AgentMessage) -> None:
        """Handle a task (for critique on task structure)"""
        task = message.payload.get("task", "")
        # Could evaluate task quality before execution
        pass

    async def evaluate(self, task: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """
        Evaluate a task result.

        This is a simplified implementation. In production, this could use
        an LLM to perform more sophisticated evaluation.

        Args:
            task: Task information
            result: The result to evaluate

        Returns:
            Evaluation dictionary with scores and feedback
        """
        # Simple heuristic evaluation
        scores = []
        feedback_parts = []

        # Check if result exists
        if result is None:
            return {
                "scores": [0.0],
                "passed": False,
                "feedback": "No result provided",
            }

        # Check result type
        if isinstance(result, str):
            # String result - check length and content
            if len(result) == 0:
                scores.append(0.0)
                feedback_parts.append("Empty result")
            elif len(result) < 10:
                scores.append(0.3)
                feedback_parts.append("Result too short")
            else:
                scores.append(0.8)
                feedback_parts.append("Result appears adequate")

        elif isinstance(result, dict):
            # Dict result - check for required fields
            required_fields = ["content", "data", "result"]
            has_field = any(field in result for field in required_fields)
            if has_field:
                scores.append(0.8)
                feedback_parts.append("Result structure OK")
            else:
                scores.append(0.5)
                feedback_parts.append("Result missing common fields")

        elif isinstance(result, (list, tuple)):
            # List result
            if len(result) == 0:
                scores.append(0.3)
                feedback_parts.append("Empty list")
            else:
                scores.append(0.7)
                feedback_parts.append(f"List with {len(result)} items")

        else:
            scores.append(0.6)
            feedback_parts.append(f"Result type: {type(result).__name__}")

        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        passed = overall_score >= self.threshold

        return {
            "task_id": task.get("task_id"),
            "scores": scores,
            "overall_score": overall_score,
            "passed": passed,
            "feedback": "; ".join(feedback_parts),
            "threshold": self.threshold,
        }

    def get_criteria(self, task_type: str) -> List[str]:
        """
        Get evaluation criteria for a task type.

        Args:
            task_type: Type of task

        Returns:
            List of criteria descriptions
        """
        # Domain-specific criteria
        criteria_map = {
            "code": [
                "Code compiles without errors",
                "Code follows style guidelines",
                "Code has appropriate comments",
                "Code handles edge cases",
            ],
            "code-review": [
                "Code is correct",
                "Code is efficient",
                "Code is readable",
                "Code is secure",
            ],
            "document-analysis": [
                "Analysis is thorough",
                "Key points identified",
                "Conclusions supported",
            ],
            "debate": [
                "Arguments are logical",
                "Evidence provided",
                "Counterarguments addressed",
            ],
        }
        return criteria_map.get(self.domain, ["General quality check"])

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        base_status = super().get_status()
        base_status.update({
            "domain": self.domain,
            "threshold": self.threshold,
            "evaluations_count": sum(len(v) for v in self._evaluation_history.values()),
        })
        return base_status
