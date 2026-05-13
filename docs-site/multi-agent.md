# Multi-Agent Collaboration System

> **Note**: This is the design specification for the Multi-Agent Collaboration System (P-20260513-002).

## Overview

The Multi-Agent Collaboration System enables multiple specialized AI agents to work together on complex tasks. It provides task decomposition, parallel execution, and result aggregation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Event Loop (asyncio)                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Message Queue (asyncio.Queue)               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Coordinator  │  │ Specialist   │  │   Critic     │ │ │
│  │  │   Agent      │  │   Agent (xN) │  │   Agent      │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  ContextPool (shared memory)            │ │
│  │       tasks │ memories │ results                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### MessageQueue

The `MessageBus` class provides inter-agent communication using `asyncio.Queue`.

```python
from astrbot.core.multi_agent import MessageBus, AgentMessage, MessageType

message_bus = MessageBus()

# Subscribe to topics
await message_bus.subscribe("agent-1", ["task", "result"])

# Publish a message
message = AgentMessage(
    sender="agent-1",
    recipient="agent-2",
    type=MessageType.TASK,
    payload={"task": "analyze this code"}
)
await message_bus.publish(message)

# Get message for specific agent
msg = await message_bus.get("agent-2", timeout=5.0)
```

### ContextPool

Shared memory for task state and cross-agent information sharing.

```python
from astrbot.core.multi_agent import ContextPool, TaskNode

context_pool = ContextPool()

# Store data
await context_pool.put("shared-key", {"result": "data"}, ttl=3600)

# Get data
data = await context_pool.get("shared-key")

# Manage tasks
task = TaskNode(type="task", status="pending")
await context_pool.add_task(task)
await context_pool.update_task_status(task.id, "running")
```

### Agent Types

#### BaseAgent

Abstract base class for all agents.

```python
from astrbot.core.multi_agent import BaseAgent

class MyAgent(BaseAgent):
    async def handle_message(self, message: AgentMessage):
        # Handle incoming messages
        pass
```

#### CoordinatorAgent

Decomposes tasks and schedules specialist agents.

```python
from astrbot.core.multi_agent import CoordinatorAgent

coordinator = CoordinatorAgent(
    agent_id="coordinator",
    name="MainCoordinator",
    message_bus=message_bus,
    context_pool=context_pool
)
```

#### SpecialistAgent

Executes domain-specific tasks.

```python
from astrbot.core.multi_agent import SpecialistAgent

class CodeGenerator(SpecialistAgent):
    async def execute(self, task: Dict) -> Any:
        # Generate code based on task description
        return {"code": "..."}
```

#### CriticAgent

Evaluates results and provides quality feedback.

```python
from astrbot.core.multi_agent import CriticAgent

critic = CriticAgent(
    agent_id="critic",
    name="QualityCritic",
    domain="code-quality",
    message_bus=message_bus,
    context_pool=context_pool,
    threshold=0.7
)
```

## Built-in Teams

### CodeReviewTeam

```python
from astrbot.core.multi_agent import CodeReviewTeam

team = CodeReviewTeam()
await team.start()
result = await team.execute("Review this function: def foo(x): return x + 1")
await team.stop()
```

**Agents**: Coordinator + CodeGenerator + CodeReviewer + CodeCritic

### ResearchTeam

```python
from astrbot.core.multi_agent import ResearchTeam

team = ResearchTeam()
await team.start()
result = await team.execute("Research quantum computing applications")
await team.stop()
```

**Agents**: Coordinator + WebSearcher + DocAnalyzer + Synthesizer

### DebateTeam

```python
from astrbot.core.multi_agent import DebateTeam

team = DebateTeam()
await team.start()
result = await team.execute("Should AI be regulated?")
await team.stop()
```

**Agents**: Coordinator + ProArguer + ConArguer + DebateJudge

## API Reference

### POST `/api/multi-agent/execute`

Execute a multi-agent task.

**Request:**
```json
{
  "team": "code-review",
  "task": "Review this code: def foo(): pass"
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "status": "started",
  "team": "code-review",
  "message": "Task is being processed"
}
```

### GET `/api/multi-agent/status/{task_id}`

Get task status.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "running",
  "team": "code-review",
  "task": "Review this code..."
}
```

### GET `/api/multi-agent/memory/{task_id}`

Get context pool snapshot.

**Response:**
```json
{
  "task_id": "uuid",
  "snapshot": {
    "storage": {},
    "tasks": {},
    "subscriptions": []
  }
}
```

### GET `/api/multi-agent/teams`

List available team types.

**Response:**
```json
{
  "teams": [
    {
      "id": "code-review",
      "name": "Code Review Team",
      "agents": ["coordinator", "code-generator", "code-reviewer", "code-critic"]
    }
  ]
}
```

### DELETE `/api/multi-agent/task/{task_id}`

Cancel a running task.

## Configuration

```python
from astrbot.core.multi_agent import MultiAgentConfig, AgentConfig

config = MultiAgentConfig(
    enabled=True,
    max_parallel=5,
    timeout=300.0,
    retry=3,
    default_team="code-review"
)

# Add custom team
config.add_team("my-team", [
    AgentConfig(id="coord", name="Coordinator", type="coordinator"),
    AgentConfig(id="spec1", name="Specialist1", type="specialist", domain="domain1"),
])
```

## Dashboard

The Multi-Agent Dashboard (`MultiAgentDashboard.vue`) provides:

- **Team Selection**: Choose from pre-configured teams
- **Task Execution**: Submit tasks for processing
- **Task Graph Visualization**: See task dependencies
- **Agent Status Monitor**: View all agent states
- **Message Flow Display**: Track inter-agent messages

## Message Types

| Type | Description |
|------|-------------|
| `TASK` | Task assignment |
| `RESULT` | Task result |
| `CRITIQUE` | Quality evaluation |
| `STOP` | Termination signal |
| `HEARTBEAT` | Agent heartbeat |

## Task Lifecycle

```
pending → running → done
                  ↘ failed
         ↘ cancelled
```

## Error Handling

```python
from astrbot.core.multi_agent import (
    MultiAgentError,
    TaskTimeoutError,
    AgentNotFoundError,
    TaskNotFoundError,
    CyclicDependencyError
)

try:
    result = await team.execute(task)
except TaskTimeoutError as e:
    print(f"Task {e.task_id} timed out after {e.timeout}s")
except AgentNotFoundError as e:
    print(f"Agent {e.agent_id} not found")
```

## Usage Example

Complete example with all components:

```python
import asyncio
from astrbot.core.multi_agent import (
    CodeReviewTeam,
    MessageBus,
    ContextPool,
    AgentMessage,
    MessageType
)

async def main():
    # Create shared infrastructure
    message_bus = MessageBus()
    context_pool = ContextPool()
    
    # Create and start team
    team = CodeReviewTeam(
        message_bus=message_bus,
        context_pool=context_pool
    )
    await team.start()
    
    try:
        # Execute task
        result = await team.execute("Review this code: def add(a, b): return a + b")
        print(f"Result: {result}")
        
        # Get team status
        status = team.get_status()
        print(f"Team status: {status}")
        
        # Get context snapshot
        snapshot = await context_pool.snapshot()
        print(f"Context: {snapshot}")
        
    finally:
        await team.stop()

asyncio.run(main())
```

## Testing

Run the test suite:

```bash
cd /home/hermes/workspace-dev/proposals/astrbot-design
python3 -m pytest tests/unit/ -v -k "multi_agent"
```

Or test manually:

```bash
python3 -c "
import asyncio
from astrbot.core.multi_agent import CodeReviewTeam

async def test():
    team = CodeReviewTeam()
    await team.start()
    result = await team.execute('Review: def hello(): print(\"world\")')
    print('Result:', result)
    await team.stop()

asyncio.run(test())
"
```

## Future Enhancements

- LLM-powered task decomposition
- Dynamic agent spawning
- Distributed message bus (Redis-based)
- Advanced conflict resolution
- Performance metrics and monitoring
