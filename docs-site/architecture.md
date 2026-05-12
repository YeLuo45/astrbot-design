# AstrBot Architecture Analysis

## 1. System Overview

AstrBot is a modular AI Agent framework supporting multiple chat platforms, LLM providers, and extensible plugin system.

**Key Characteristics**:
- Python 3.10+ backend with asyncio
- FastAPI-based HTTP API (v4.18.0+)
- Vue 3 + Vuetify management dashboard
- 20+ LLM providers, 15+ IM platforms
- Star/Plugin extension system

## 2. Core Modules

### 2.1 astrbot/core - Core Engine

| Module | Path | Description |
|--------|------|-------------|
| **agent** | `core/agent/` | Agent execution engine, context management, tool execution |
| **pipeline** | `core/pipeline/` | Message processing pipeline (preprocess → process → respond) |
| **provider** | `core/provider/` | LLM provider abstraction layer (20+ providers) |
| **platform** | `core/platform/` | Multi-platform adapter system (15+ platforms) |
| **skills** | `core/skills/` | Skill management system |
| **knowledge_base** | `core/kb/` | RAG knowledge base with FAISS |
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
- Chat operations (SSE streaming)
- Plugin management
- Knowledge base
- Session management
- Platform/bot configuration
- File upload

### 2.4 dashboard - WebUI

Vue 3 + Vuetify 3 + TypeScript management dashboard with:
- Authentication (JWT-based)
- Provider/Platform/Plugin management
- Knowledge base configuration
- Persona management
- Session/Conversation management

## 3. Key Design Patterns

### 3.1 Provider Pattern

```
Provider (abstract base class)
├── OpenAISource
├── AnthropicSource
├── DashscopeSource
├── GeminiSource
├── OllamaSource
├── SiliconFlowSource
├── NewAPISource
└── ... (20+ providers)
```

### 3.2 Platform Adapter Pattern

```
Platform (abstract base class)
├── TelegramAdapter
├── DiscordAdapter
├── QQOfficialAdapter
├── QQGroupAdapter
├── WechatAdapter
├── WechatOfficialAccountAdapter
├── LarkAdapter
├── FeishuAdapter
├── DingTalkAdapter
├── KOOKAdapter
├── SlackAdapter
├── VOICEChatAdapter
├── SatoriAdapter
├── AiocqhttpAdapter
└── ... (15+ platforms)
```

### 3.3 Pipeline Pattern

```
Message → Preprocess → Content Safety → Rate Limit → Wake Check
       → Agent (LLM + Tools)
       → Respond → Result Decorate
       → Platform Adapter → Output
```

### 3.4 Star/Plugin Pattern

Extension system with:
- `metadata.yaml` - Plugin metadata (name, version, dependencies)
- `i18n/` - Internationalization files
- `main.py` - Entry point (StarBase subclass)
- `.astrbot-plugin/` - Marker directory

**Plugin Capabilities**:
- Custom commands
- Web pages (embedded in dashboard)
- Scheduled tasks (Cron)
- Event handlers

## 4. Data Flow

```
User Message (any IM platform)
    ↓
Platform Adapter (converts to AStrBotMessage)
    ↓
Pipeline: Preprocess → Content Safety → Rate Limit → Wake Check
    ↓
Agent (LLM + Tools + Skills)
    ↓
Pipeline: Respond → Result Decorate
    ↓
Platform Adapter (converts to platform-specific format)
    ↓
User Response
```

## 5. Extension Points

### 5.1 Stars (Plugins)
- Location: `~/.astrbot/stars/`
- Interface: `astrbot.api.star.v1.StarBase`
- Capabilities: Commands, web pages, scheduled tasks, event handlers

### 5.2 Tools
- Built-in: web_search, file_system, shell, python, browser
- Custom: via MCP server or plugin-provided

### 5.3 Agent Runners
| Runner | Description |
|--------|-------------|
| ToolLoopAgentRunner | Default tool-use loop |
| CozeAgentRunner | Coze bot integration |
| DeerFlowAgentRunner | DeerFlow workflow |
| DifyAgentRunner | Dify workflow |

### 5.4 Skills System
Structured prompts for specialized tasks:
- Location: `~/.astrbot/skills/`
- YAML-based definition
- Hot-reloadable

## 6. Technology Stack

| Layer | Technology |
|-------|------------|
| Core | Python 3.10+, asyncio, uv |
| API | FastAPI, uvicorn, SSE |
| Database | SQLite + FAISS |
| Frontend | Vue 3, Vuetify 3, TypeScript, Pinia |
| Package | uv (Python), pnpm (Node) |
| Container | Docker, Docker Compose |
| Orchestration | Kubernetes, 1Panel |

## 7. Project Structure

```
astrbot/
├── main.py                 # Application entry point
├── runtime_bootstrap.py     # Runtime initialization
├── pyproject.toml          # Python dependencies
│
├── astrbot/
│   ├── api/                # FastAPI endpoints
│   │   ├── chat.py
│   │   ├── im.py
│   │   ├── file.py
│   │   ├── config.py
│   │   └── star/           # Plugin API
│   │
│   ├── core/                # Core engine
│   │   ├── agent/           # Agent logic
│   │   ├── computer/        # Computer use (shell/python/browser)
│   │   ├── config/          # Configuration
│   │   ├── kb/              # Knowledge base (FAISS)
│   │   ├── platform/        # Platform adapters
│   │   ├── pipeline/        # Message pipeline
│   │   ├── provider/        # LLM providers
│   │   ├── skills/          # Skills system
│   │   ├── tools/           # Tool registry
│   │   ├── db/              # Database
│   │   └── cron/            # Cron system
│   │
│   ├── builtin_stars/       # Built-in extensions
│   │   ├── astrbot/          # Core bot
│   │   └── builtin_commands/ # Built-in commands
│   │
│   └── dashboard/           # WebUI (Vue)
│       ├── src/
│       └── dist/            # Built assets
│
├── tests/                   # Test suite
├── docs/                    # Official documentation
└── compose.yml              # Docker Compose
```

## 8. Configuration

| Config Type | Location |
|-------------|----------|
| Default config | `astrbot/core/config/default.py` |
| User config | `~/.astrbot/config.yaml` |
| Platform configs | `astrbot/core/platform/sources/` |
| Plugin config | `~/.astrbot/stars/<plugin>/config.yaml` |

## 9. Key Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point, initializes all components |
| `runtime_bootstrap.py` | Runtime initialization, DI container setup |
| `pyproject.toml` | Python dependencies (uv format) |
| `AGENTS.md` | Developer guide |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `compose.yml` | Docker Compose deployment |
