"""
Multi-Agent Collaboration System - Context Pool

Shared memory and task state management for multi-agent collaboration.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class TaskNode:
    """
    Represents a task node in the task graph.

    Attributes:
        id: Unique task identifier
        type: Type of node ("task", "result", "critique")
        status: Current status ("pending", "running", "done", "failed")
        result: Task result if completed
        children: List of child task IDs
        parent: Parent task ID if any
        created_at: When the task was created
        updated_at: When the task was last updated
        metadata: Additional task metadata
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "task"
    status: str = "pending"
    result: Any = None
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task node to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "result": self.result,
            "children": self.children,
            "parent": self.parent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskNode":
        """Create task node from dictionary"""
        data = data.copy()
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class ContextPool:
    """
    Shared context pool for multi-agent collaboration.

    Provides:
    - Key-value storage with TTL
    - Task graph management
    - Pub/sub for context changes
    - Atomic operations
    """

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the context pool.

        Args:
            default_ttl: Default time-to-live for entries in seconds
        """
        self.default_ttl = default_ttl
        # Key-value storage with optional TTL
        self._storage: Dict[str, Any] = {}
        self._storage_ttl: Dict[str, float] = {}
        # Task nodes
        self._tasks: Dict[str, TaskNode] = {}
        # Subscriptions for context changes
        self._subscriptions: Dict[str, asyncio.Queue] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the context pool.

        Args:
            key: The key to store under
            value: The value to store
            ttl: Time-to-live in seconds (None = use default)
        """
        async with self._lock:
            self._storage[key] = value
            import time
            ttl_val = ttl if ttl is not None else self.default_ttl
            self._storage_ttl[key] = time.time() + ttl_val
            await self._notify_subscribers(key, value)

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the context pool.

        Args:
            key: The key to retrieve

        Returns:
            The stored value, or None if not found or expired
        """
        async with self._lock:
            import time
            if key in self._storage:
                if key in self._storage_ttl:
                    if time.time() > self._storage_ttl[key]:
                        # Expired
                        del self._storage[key]
                        del self._storage_ttl[key]
                        return None
                return self._storage[key]
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from the context pool.

        Args:
            key: The key to delete

        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if key in self._storage:
                del self._storage[key]
                if key in self._storage_ttl:
                    del self._storage_ttl[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired"""
        value = await self.get(key)
        return value is not None

    async def subscribe(self, key: str) -> asyncio.Queue:
        """
        Subscribe to changes for a key.

        Args:
            key: The key to subscribe to

        Returns:
            Queue that will receive notifications
        """
        async with self._lock:
            if key not in self._subscriptions:
                self._subscriptions[key] = asyncio.Queue()
            return self._subscriptions[key]

    async def unsubscribe(self, key: str) -> None:
        """
        Unsubscribe from a key.

        Args:
            key: The key to unsubscribe from
        """
        async with self._lock:
            if key in self._subscriptions:
                del self._subscriptions[key]

    async def _notify_subscribers(self, key: str, value: Any) -> None:
        """Notify subscribers of a change"""
        if key in self._subscriptions:
            try:
                await self._subscriptions[key].put(value)
            except Exception:
                pass

    # Task graph operations

    async def add_task(self, task: TaskNode) -> None:
        """
        Add a task to the task graph.

        Args:
            task: The task to add
        """
        async with self._lock:
            self._tasks[task.id] = task

    async def get_task(self, task_id: str) -> Optional[TaskNode]:
        """
        Get a task by ID.

        Args:
            task_id: The task ID

        Returns:
            The task node, or None if not found
        """
        async with self._lock:
            return self._tasks.get(task_id)

    async def update_task_status(
        self, task_id: str, status: str, result: Any = None
    ) -> None:
        """
        Update a task's status.

        Args:
            task_id: The task ID
            status: New status ("pending", "running", "done", "failed")
            result: Optional result to store
        """
        async with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = status
                task.updated_at = datetime.now()
                if result is not None:
                    task.result = result
                # Also store in key-value for easy access
                self._storage[f"task:{task_id}:status"] = status
                if result is not None:
                    self._storage[f"task:{task_id}:result"] = result

    async def add_child_task(self, parent_id: str, child_id: str) -> None:
        """
        Add a child task relationship.

        Args:
            parent_id: The parent task ID
            child_id: The child task ID
        """
        async with self._lock:
            if parent_id in self._tasks and child_id in self._tasks:
                self._tasks[parent_id].children.append(child_id)
                self._tasks[child_id].parent = parent_id

    async def get_child_tasks(self, task_id: str) -> List[TaskNode]:
        """
        Get all child tasks of a task.

        Args:
            task_id: The parent task ID

        Returns:
            List of child task nodes
        """
        async with self._lock:
            if task_id in self._tasks:
                child_ids = self._tasks[task_id].children
                return [self._tasks[cid] for cid in child_ids if cid in self._tasks]
            return []

    async def get_parent_task(self, task_id: str) -> Optional[TaskNode]:
        """
        Get the parent task of a task.

        Args:
            task_id: The child task ID

        Returns:
            The parent task node, or None
        """
        async with self._lock:
            if task_id in self._tasks:
                parent_id = self._tasks[task_id].parent
                if parent_id:
                    return self._tasks.get(parent_id)
            return None

    async def get_root_tasks(self) -> List[TaskNode]:
        """
        Get all root tasks (tasks with no parent).

        Returns:
            List of root task nodes
        """
        async with self._lock:
            return [task for task in self._tasks.values() if task.parent is None]

    async def get_task_tree(self, root_id: str) -> Dict[str, Any]:
        """
        Get a task tree starting from a root task.

        Args:
            root_id: The root task ID

        Returns:
            Dictionary representing the task tree
        """
        async with self._lock:
            if root_id not in self._tasks:
                return {}

            def build_tree(task_id: str) -> Dict[str, Any]:
                task = self._tasks[task_id]
                return {
                    "id": task.id,
                    "type": task.type,
                    "status": task.status,
                    "result": task.result,
                    "metadata": task.metadata,
                    "children": [build_tree(cid) for cid in task.children if cid in self._tasks],
                }

            return build_tree(root_id)

    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task and its descendants.

        Args:
            task_id: The task ID to delete

        Returns:
            True if deleted
        """
        async with self._lock:
            if task_id not in self._tasks:
                return False

            # Recursively delete children
            def delete_descendants(tid: str):
                if tid in self._tasks:
                    for child_id in self._tasks[tid].children:
                        delete_descendants(child_id)
                    del self._tasks[tid]

            delete_descendants(task_id)
            return True

    async def get_all_tasks(self) -> List[TaskNode]:
        """Get all tasks"""
        async with self._lock:
            return list(self._tasks.values())

    async def get_tasks_by_status(self, status: str) -> List[TaskNode]:
        """Get all tasks with a specific status"""
        async with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    async def clear_expired(self) -> int:
        """
        Clear expired storage entries.

        Returns:
            Number of entries cleared
        """
        import time
        async with self._lock:
            expired_keys = [
                key for key, expiry in self._storage_ttl.items()
                if time.time() > expiry
            ]
            for key in expired_keys:
                del self._storage[key]
                del self._storage_ttl[key]
            return len(expired_keys)

    async def snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the entire context pool.

        Returns:
            Dictionary containing all storage and tasks
        """
        async with self._lock:
            return {
                "storage": dict(self._storage),
                "tasks": {tid: task.to_dict() for tid, task in self._tasks.items()},
                "subscriptions": list(self._subscriptions.keys()),
            }
