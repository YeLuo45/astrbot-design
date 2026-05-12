# AstrBot Architecture Analysis

## 1. System Overview

AstrBot is a modular AI Agent framework supporting multiple chat platforms, LLM providers, and extensible plugin system.

## 2. Core Modules

### 2.1 astrbot/core - Core Engine

| Module | Path | Description |
|--------|------|-------------|
| **agent** | `core/agent/` | Agent execution engine, context management, tool execution |
| **pipeline** | `core/pipeline/` | Message processing pipeline (preprocess → process → respond) |
| **provider** | `core/provider/` | LLM provider abstraction layer |
| **platform** | `core/platform/` | Multi-platform adapter system |
| **skills** | `core/skills/` | Skill management system |
| **knowledge_base** | `core/knowledge_base/` | RAG knowledge base with FAISS |
| **computer** | `core/computer/` | Computer use tools (shell, python, browser) |
| **tools** | `core/tools/` | Tool registry and implementations |
| **db** | `core/db/` | SQLite + FAISS vector database |
| **cron** | `core/cron/` | Scheduled task system |
| **config** | `core/config/` | Configuration management |

### 2.2 astrbot/builtin_stars - Built-in Extensions

| Module | Path | Description |
|--------|------|-------------|
| **astrbot** | `builtin_stars/astrbot/` | Core bot functionality (long-term memory) |
| **builtin_commands** | `builtin_stars/builtin_commands/` | Admin, help, provider, conversation commands |

### 2.3 astrbot/api - Public API

FastAPI-based API server exposing endpoints for:
- Chat operations
- Plugin management
- Knowledge base
- Session management
- Platform configuration

### 2.4 dashboard - WebUI

React + Vuetify + Vue 3 management dashboard.

## 3. Key Design Patterns

### 3.1 Provider Pattern
```
Provider (abstract)
├── OpenAISource
├── AnthropicSource
├── DashscopeSource
├── GeminiSource
└── ... (20+ providers)
```

### 3.2 Platform Adapter Pattern
```
Platform (abstract)
├── TelegramAdapter
├── DiscordAdapter
├── QQAdapter
├── WechatAdapter
├── LarkAdapter
└── ... (15+ platforms)
```

### 3.3 Pipeline Pattern
```
Message → Preprocess → Process (Agent) → Respond → Decorate → Output
```

### 3.4 Star/Plugin Pattern
Extension system with:
- `metadata.yaml` - Plugin definition
- `i18n/` - Internationalization
- `main.py` - Entry point
- `.astrbot-plugin/` - Marker directory

## 4. Data Flow

```
User Message
    ↓
Platform Adapter (convert to AStrBotMessage)
    ↓
Pipeline: Preprocess → Content Safety → Rate Limit → Wake Check
    ↓
Agent (LLM + Tools)
    ↓
Pipeline: Respond → Result Decorate
    ↓
Platform Adapter (convert to platform-specific format)
    ↓
User Response
```

## 5. Extension Points

### 5.1 Stars (Plugins)
- Location: `~/.astrbot/stars/`
- Interface: `astrbot.api.star.StarBase`
- Capabilities: Commands, web pages, scheduled tasks

### 5.2 Tools
- Built-in: web_search, file_system, shell, python, browser
- Custom: via MCP or plugin-provided

### 5.3 Agent Runners
- ToolLoopAgentRunner (default)
- CozeAgentRunner
- DeerFlowAgentRunner
- DifyAgentRunner

## 6. Technology Stack

| Layer | Technology |
|-------|------------|
| Core | Python 3.10+, asyncio |
| API | FastAPI, uvicorn |
| Database | SQLite + FAISS |
| Frontend | React 3, Vuetify 3, TypeScript |
| Package | uv (Python), pnpm (Node) |
| Container | Docker, Docker Compose |
| Orchestration | Kubernetes |

## 7. Directory Structure

```
astrbot/
├── api/              # FastAPI endpoints
├── builtin_stars/    # Built-in extensions
├── cli/              # CLI commands
├── core/             # Core engine
│   ├── agent/        # Agent logic
│   ├── computer/      # Computer use
│   ├── config/       # Configuration
│   ├── knowledge_base/ # RAG
│   ├── platform/     # Platform adapters
│   ├── pipeline/     # Processing pipeline
│   ├── provider/     # LLM providers
│   ├── skills/       # Skills system
│   └── tools/        # Tool registry
├── dashboard/        # WebUI (Vue)
├── docs/             # Documentation
├── tests/            # Test suite
└── main.py           # Entry point
```

## 8. Configuration

- Default config: `astrbot/core/config/default.py`
- User config: `~/.astrbot/config.yaml`
- Platform-specific configs in `astrbot/core/platform/sources/`

## 9. Key Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `runtime_bootstrap.py` | Runtime initialization |
| `pyproject.toml` | Python dependencies |
| `AGENTS.md` | Developer guide |
| `.pre-commit-config.yaml` | Pre-commit hooks |
