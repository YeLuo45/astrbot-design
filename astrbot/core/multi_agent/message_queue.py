"""
Multi-Agent Collaboration System - Message Queue

Implements the MessageBus for inter-agent communication using asyncio.Queue.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class MessageType(Enum):
    """Types of messages in the multi-agent system"""

    TASK = "task"
    RESULT = "result"
    CRITIQUE = "critique"
    STOP = "stop"
    HEARTBEAT = "heartbeat"


@dataclass
class AgentMessage:
    """
    Represents a message passed between agents.

    Attributes:
        id: Unique message identifier
        sender: ID of the sending agent
        recipient: ID of receiving agent (None for broadcast)
        type: Type of message (task, result, critique, stop, heartbeat)
        payload: Message content as dictionary
        timestamp: When the message was created
        correlation_id: Used to correlate request/response pairs
        reply_to: ID of the message this is replying to
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: Optional[str] = None
    type: MessageType = MessageType.TASK
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        data = data.copy()
        if "type" in data and isinstance(data["type"], str):
            data["type"] = MessageType(data["type"])
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MessageBus:
    """
    Asyncio-based message bus for inter-agent communication.

    Supports:
    - Point-to-point messaging (send to specific agent)
    - Broadcast messaging (send to all subscribed agents)
    - Topic-based subscription
    """

    def __init__(self):
        # Maps agent_id -> Queue of messages for that agent
        self._agent_queues: Dict[str, asyncio.Queue] = {}
        # Maps topic -> set of agent_ids subscribed to that topic
        self._subscriptions: Dict[str, Set[str]] = {}
        # Global broadcast queue
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def subscribe(self, agent_id: str, topics: List[str]) -> None:
        """
        Subscribe an agent to specific topics.

        Args:
            agent_id: ID of the agent to subscribe
            topics: List of topic names to subscribe to
        """
        async with self._lock:
            # Ensure agent has a queue
            if agent_id not in self._agent_queues:
                self._agent_queues[agent_id] = asyncio.Queue()

            # Subscribe to each topic
            for topic in topics:
                if topic not in self._subscriptions:
                    self._subscriptions[topic] = set()
                self._subscriptions[topic].add(agent_id)

    async def unsubscribe(self, agent_id: str, topics: Optional[List[str]] = None) -> None:
        """
        Unsubscribe an agent from topics.

        Args:
            agent_id: ID of the agent to unsubscribe
            topics: List of topics to unsubscribe from (None = all)
        """
        async with self._lock:
            if topics is None:
                # Unsubscribe from all topics
                for topic in self._subscriptions:
                    self._subscriptions[topic].discard(agent_id)
            else:
                for topic in topics:
                    if topic in self._subscriptions:
                        self._subscriptions[topic].discard(agent_id)

    async def publish(self, message: AgentMessage) -> None:
        """
        Publish a message to the message bus.

        Args:
            message: The message to publish
        """
        async with self._lock:
            if message.recipient is None:
                # Broadcast to all subscribers of the message type
                topic = message.type.value
                if topic in self._subscriptions:
                    for agent_id in self._subscriptions[topic]:
                        await self._agent_queues[agent_id].put(message)
                # Also put in broadcast queue
                await self._broadcast_queue.put(message)
            else:
                # Point-to-point message
                if message.recipient in self._agent_queues:
                    await self._agent_queues[message.recipient].put(message)
                else:
                    # Agent not found - could raise exception or handle gracefully
                    raise Exception(f"Agent {message.recipient} not found")

    async def get(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Get the next message for an agent.

        Args:
            agent_id: ID of the agent
            timeout: Optional timeout in seconds

        Returns:
            The next message, or None if timeout
        """
        if agent_id not in self._agent_queues:
            self._agent_queues[agent_id] = asyncio.Queue()

        try:
            if timeout is None:
                return await self._agent_queues[agent_id].get()
            else:
                return await asyncio.wait_for(
                    self._agent_queues[agent_id].get(), timeout=timeout
                )
        except asyncio.TimeoutError:
            return None

    async def put(self, agent_id: str, message: AgentMessage) -> None:
        """
        Put a message directly into an agent's queue.

        Args:
            agent_id: ID of the target agent
            message: The message to deliver
        """
        async with self._lock:
            if agent_id not in self._agent_queues:
                self._agent_queues[agent_id] = asyncio.Queue()
            await self._agent_queues[agent_id].put(message)

    def get_subscribers(self, topic: str) -> Set[str]:
        """Get all agents subscribed to a topic"""
        return self._subscriptions.get(topic, set()).copy()

    def get_queue_size(self, agent_id: str) -> int:
        """Get the number of messages waiting for an agent"""
        if agent_id in self._agent_queues:
            return self._agent_queues[agent_id].qsize()
        return 0

    async def clear(self, agent_id: Optional[str] = None) -> None:
        """
        Clear all messages from queues.

        Args:
            agent_id: If provided, only clear that agent's queue
        """
        async with self._lock:
            if agent_id is None:
                for queue in self._agent_queues.values():
                    while not queue.empty():
                        try:
                            queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break
            elif agent_id in self._agent_queues:
                queue = self._agent_queues[agent_id]
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
