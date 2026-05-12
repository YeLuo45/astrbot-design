# AstrBot Plugin Development Guide

> **Plugin = Star.** AstrBot internally calls plugins "Stars". The handler system is called "star_handler".

## Table of Contents

1. [Plugin System Overview](#1-plugin-system-overview)
2. [Project Structure](#2-project-structure)
3. [Plugin Metadata (metadata.yaml)](#3-plugin-metadata-metadatayaml)
4. [The Star Base Class](#4-the-star-base-class)
5. [Event Handlers](#5-event-handlers)
6. [Command Handlers](#6-command-handlers)
7. [Context API](#7-context-api)
8. [LLM/Tool Integration](#8-llmtool-integration)
9. [Plugin Pages (Dashboard Integration)](#9-plugin-pages-dashboard-integration)
10. [Internationalization (i18n)](#10-internationalization-i18n)
11. [Plugin Lifecycle](#11-plugin-lifecycle)
12. [Complete Example: Hello World](#12-complete-example-hello-world)
13. [Plugin Loading & Management](#13-plugin-loading--management)
14. [Filter Reference](#14-filter-reference)
15. [Event Type Reference](#15-event-type-reference)

---

## 1. Plugin System Overview

AstrBot's plugin system ("Star") is a modular extension architecture that allows developers to add new capabilities without modifying core code.

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Star** | Plugin class — all plugins inherit from `Star` |
| **StarHandler** | Individual handler methods within a Star |
| **EventType** | Type of event that triggers a handler |
| **HandlerFilter** | Condition that determines if a handler should respond |
| **Context** | Runtime context passed to Star, provides all APIs |
| **metadata.yaml** | Plugin descriptor file |

### Handler Execution Flow

```
User Message
    ↓
Platform Adapter → AstrMessageEvent
    ↓
Handler Dispatch (star_handlers_registry)
    ↓
Filter Check (CommandFilter / RegexFilter / etc.)
    ↓
Handler Method Called
    ↓
Optional: stop_event() to prevent further handlers
```

### Key Files

| File | Purpose |
|------|---------|
| `astrbot/core/star/base.py` | `Star` base class |
| `astrbot/core/star/star.py` | `StarMetadata`, `star_registry`, `star_map` |
| `astrbot/core/star/star_handler.py` | `EventType`, `StarHandlerRegistry`, `star_handlers_registry` |
| `astrbot/core/star/register/__init__.py` | All `@register_*` decorators |
| `astrbot/core/star/register/star_handler.py` | Registration decorator implementations |
| `astrbot/core/star/filter/` | Handler filters: Command, Regex, Permission, etc. |
| `astrbot/core/star/context.py` | `Context` class — all plugin-facing APIs |
| `astrbot/core/star/star_manager.py` | Plugin lifecycle (load/unload/reload/install) |
| `astrbot/api/star/__init__.py` | Public plugin API (`from astrbot.api import star`) |

---

## 2. Project Structure

A plugin lives in `data/stars/` (or `stars/` in dev mode):

```
data/stars/
└── my_plugin/
    ├── __init__.py        # Plugin entry point (can be empty)
    ├── main.py            # Plugin code — contains the Star class
    ├── metadata.yaml      # Plugin descriptor (required)
    ├── requirements.txt   # Optional pip dependencies
    ├── i18n/              # Optional internationalization
    │   ├── en.json
    │   └── zh.json
    └── assets/            # Optional static assets
        └── icon.png
```

### metadata.yaml (required)

```yaml
name: my_plugin            # Unique plugin identifier
desc: A short description  # One-line description
author: Author Name
version: 1.0.0
astrbot_version: ">=4.0.0" # PEP 440 specifier, e.g. ">=4.13.0,<4.17.0"
                             # If omitted, any AstrBot version is accepted
```

**Optional fields:**

```yaml
short_desc: Short description  # For plugin store display
repo: https://github.com/user/repo  # Plugin repo URL
logo_path: assets/icon.png       # Relative to plugin root
support_platforms:               # Restrict to specific platforms
  - qq
  - telegram
i18n:                             # Inline i18n translations
  en:
    greeting: "Hello"
  zh:
    greeting: "你好"
```

---

## 3. Plugin Metadata (metadata.yaml)

The `metadata.yaml` file is the plugin's identity card. It is read by `StarManager` during plugin loading.

### Minimal Example

```yaml
name: hello_world
desc: A simple hello world plugin
author: Developer
version: 1.0.0
```

### Full Example

```yaml
name: image_generator
desc: Generate images using AI
author: AstrBot Team
version: 2.1.0
astrbot_version: ">=4.13.0,<5.0.0"
short_desc: AI image generation
repo: https://github.com/astrbot/image-generator
logo_path: assets/logo.png
support_platforms:
  - qq
  - telegram
  - feishu
i18n:
  en:
    generating: "Generating image..."
    done: "Image ready!"
  zh:
    generating: "正在生成图片..."
    done: "图片已就绪！"
```

---

## 4. The Star Base Class

All plugins inherit from `Star`. It provides the plugin context, utility methods, and lifecycle hooks.

```python
from astrbot.api import star

class MyPlugin(star.Star):
    def __init__(self, context: star.Context, config: dict | None = None) -> None:
        super().__init__(context, config)
        # Initialization code here
```

### Inherited Mixins

`Star` inherits from two mixins providing key capabilities:

```python
class Star(CommandParserMixin, PluginKVStoreMixin):
    # CommandParserMixin: enables command parsing utilities
    # PluginKVStoreMixin: enables persistent key-value storage
```

### Available Attributes & Methods

| Attribute/Method | Description |
|-------------------|-------------|
| `self.context` | `Context` object — all plugin APIs |
| `self.context.get_config(umo=None)` | Get platform/user configuration |
| `self.text_to_image(text, return_url=True)` | Render text as image |
| `self.html_render(tmpl, data, return_url=True, options=None)` | Render custom HTML template |
| `async def initialize()` | Called when plugin is activated |
| `async def terminate()` | Called when plugin is deactivated/reloaded |

### Plugin KV Store

Plugins can persist data using the built-in KV store:

```python
# Inside a Star method
await self.context.get_storage().set("user_count", 0)
count = await self.context.get_storage().get("user_count")
```

---

## 5. Event Handlers

Event handlers are methods decorated with `@register_*` that respond to specific events. The most common is `@filter.event_message_type()`.

### 5.1 Message Type Filter

Respond to messages of a specific type:

```python
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Image, Plain

class MyPlugin(star.Star):
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_all(self, event: AstrMessageEvent):
        """Handles all message types"""
        pass

    @filter.event_message_type(filter.EventMessageType.TEXT)
    async def handle_text(self, event: AstrMessageEvent):
        """Handles only text messages"""
        pass

    @filter.event_message_type(filter.EventMessageType.IMAGE)
    async def handle_image(self, event: AstrMessageEvent):
        """Handles only image messages"""
        pass
```

**Available EventMessageTypes:**

```python
filter.EventMessageType.ALL         # All message types
filter.EventMessageType.TEXT        # Plain text
filter.EventMessageType.IMAGE       # Images
filter.EventMessageType.VIDEO       # Videos
filter.EventMessageType.VOICE       # Voice/audio
filter.EventMessageType.FILE        # Files
filter.EventMessageType.MENTION     # @mentions
filter.EventMessageType.REPLY       # Reply messages
```

**Priority:** Handlers with higher `priority` values execute first. Use `priority=N` to control ordering:

```python
@filter.event_message_type(filter.EventMessageType.ALL, priority=100)
async def early_handler(self, event: AstrMessageEvent):
    """Executes before default priority handlers"""
    pass
```

### 5.2 Regex Filter

Respond to messages matching a regex pattern:

```python
from astrbot.api import star, register

class MyPlugin(star.Star):
    @register.register_regex(r"^hello(?:\s+(.+))?$")
    async def handle_hello(self, event: AstrMessageEvent):
        """Matches 'hello' or 'hello <name>'"""
        # The matched groups are available via event.get_message_str()
        message = event.get_message_str()
        # Extract name if present
        import re
        match = re.match(r"^hello(?:\s+(.+))?$", message)
        name = match.group(1) if match else "World"
        await event.reply(f"Hello, {name}!")
```

### 5.3 Permission Filter

Restrict handlers to users with specific permissions:

```python
from astrbot.api.event import filter, AstrMessageEvent

class MyPlugin(star.Star):
    @filter.event_message_type(filter.EventMessageType.TEXT)
    @filter.permission(filter.PermissionType.SUPERUSER)
    async def admin_only(self, event: AstrMessageEvent):
        """Only superusers can trigger this"""
        await event.reply("You have admin access!")
```

### 5.4 Platform Filter

Restrict handlers to specific platforms:

```python
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.platform import PlatformType

class MyPlugin(star.Star):
    @filter.event_message_type(filter.EventMessageType.TEXT)
    @filter.platform_adapter_type(PlatformType.QQ)
    async def qq_only(self, event: AstrMessageEvent):
        """Only responds on QQ platform"""
        await event.reply("This is QQ!")
```

### 5.5 LLM Event Hooks

Intercept LLM request/response cycle:

```python
from astrbot.api import register

class MyPlugin(star.Star):
    @register.register_on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, request):
        """Called before LLM request is made"""
        # request is a ProviderRequest object
        # Can modify messages, model, parameters
        pass

    @register.register_on_llm_response()
    async def on_llm_response(self, event: AstrMessageEvent, response):
        """Called after LLM response is received"""
        # response is a ProviderResponse object
        pass

    @register.register_on_agent_begin()
    async def on_agent_begin(self, event: AstrMessageEvent, agent):
        """Called when agent starts executing"""
        pass

    @register.register_on_agent_done()
    async def on_agent_done(self, event: AstrMessageEvent, result):
        """Called when agent finishes executing"""
        pass
```

### 5.6 System Event Hooks

```python
from astrbot.api import register

class MyPlugin(star.Star):
    @register.register_on_astrbot_loaded()
    async def on_loaded(self, event: AstrMessageEvent):
        """Called once when AstrBot finishes loading"""
        pass

    @register.register_on_plugin_loaded()
    async def on_plugin_loaded(self, event: AstrMessageEvent):
        """Called when any plugin finishes loading"""
        pass

    @register.register_on_plugin_error()
    async def on_plugin_error(self, event: AstrMessageEvent, error: Exception, handler_name: str):
        """Called when a plugin handler throws an exception"""
        pass
```

### 5.7 Combining Filters

Filters can be stacked — all conditions must pass:

```python
class MyPlugin(star.Star):
    @filter.event_message_type(filter.EventMessageType.TEXT)
    @filter.platform_adapter_type(PlatformType.QQ)
    @register.register_regex(r"^/stats")
    async def handle_stats(self, event: AstrMessageEvent):
        """QQ platform + text + /stats prefix"""
        pass
```

---

## 6. Command Handlers

Commands are the primary way users interact with plugins. AstrBot uses a decorator-based command registration system.

### 6.1 Basic Command

```python
from astrbot.api import star, register

class MyPlugin(star.Star):
    @register.register_command("hello")
    async def cmd_hello(self, event: AstrMessageEvent):
        """Say hello to the user"""
        await event.reply("Hello!")
```

Triggered by: `@bot hello`

### 6.2 Command with Parameters

Handler methods after `self` and `event` map to command arguments:

```python
@register.register_command("greet")
async def cmd_greet(self, event: AstrMessageEvent, name: str, age: int = 18):
    """Greet someone
    
    Args:
        name: Name of the person to greet
        age: Age (default: 18)
    """
    await event.reply(f"Hello {name}, you are {age} years old!")
```

Triggered by: `@bot greet Alice 25` → `"Hello Alice, you are 25 years old!"`

### Supported Parameter Types

| Type | Conversion | Notes |
|------|------------|-------|
| `str` | Direct string | Default if no type annotation |
| `int` | `int(param)` | |
| `float` | `float(param)` | |
| `bool` | `True`/`False` | Accepts `true/false/yes/no/1/0` |
| `GreedyStr` | Remaining text as one string | Must be the last parameter |
| `None` | Auto-detect | Tries int first, then string |

### 6.3 GreedyStr (All Remaining Text)

```python
from astrbot.api.event.filter.command import GreedyStr

@register.register_command("echo")
async def cmd_echo(self, event: AstrMessageEvent, text: GreedyStr):
    """Echo back all text after the command"""
    await event.reply(str(text))
```

Triggered by: `@bot echo hello world foo` → `"hello world foo"`

### 6.4 Command Aliases

```python
@register.register_command("hello", alias={"hi", "hey"})
async def cmd_hello(self, event: AstrMessageEvent):
    """Say hello — alias: hi, hey"""
    await event.reply("Hello!")
```

Triggered by: `@bot hello`, `@bot hi`, `@bot hey`

### 6.5 Command Groups (Sub-commands)

```python
class MyPlugin(star.Star):
    @register.register_command_group("user")
    async def user_group(self, event: AstrMessageEvent):
        """User management group"""
        pass

    @register.register_command("user add", sub_command="add")
    async def cmd_user_add(self, event: AstrMessageEvent, name: str):
        """Add a user: /user add <name>"""
        await event.reply(f"User {name} added!")

    @register.register_command("user remove", sub_command="remove")
    async def cmd_user_remove(self, event: AstrMessageEvent, name: str):
        """Remove a user: /user remove <name>"""
        await event.reply(f"User {name} removed!")
```

Triggered by: `@bot user add Alice`, `@bot user remove Bob`

### 6.6 Inline Filters on Commands

```python
@register.register_command("admin_only")
@register.register_permission_type(PermissionType.SUPERUSER)
async def cmd_admin(self, event: AstrMessageEvent):
    """Admin-only command"""
    await event.reply("Admin access confirmed!")
```

---

## 7. Context API

The `Context` object (`star.Context`) is passed to every Star's `__init__` and provides access to all AstrBot capabilities.

### 7.1 Sending Messages

```python
# Reply to the current message (in same chat)
await event.reply("Hello!")

# Reply with multiple components
from astrbot.api.message_components import Image, Plain
await event.reply([
    Plain("Here is your image: "),
    Image(url="https://example.com/image.png")
])

# Send to specific conversation
await self.context.send_message(
    unified_msg_origin="qq:123456",
    message=[Plain("Direct message!")],
)

# Send to channel (platform-specific)
await self.context.send_message(
    platform="telegram",
    channel_id="-1001234567890",
    message=[Plain("Channel message!")],
)
```

### 7.2 Getting Configuration

```python
# Get global config
cfg = self.context.get_config()

# Get per-platform config
cfg = self.context.get_config(umo="qq:123456")

# Access config values
api_key = cfg.get("api_key")
model_name = cfg.get("model", "gpt-4")
```

### 7.3 Conversation Management

```python
# Get current conversation ID
curr_cid = await self.context.conversation_manager.get_curr_conversation_id(
    event.unified_msg_origin
)

# Get conversation history
conversation = await self.context.conversation_manager.get_conversation(
    event.unified_msg_origin,
    curr_cid
)

# Create new conversation
new_cid = await self.context.conversation_manager.new_conversation(
    event.unified_msg_origin,
    user_id=event.get_user_id(),
)

# Get messages in conversation
messages = await self.context.conversation_manager.get_messages(
    event.unified_msg_origin,
    curr_cid,
    limit=20,
)
```

### 7.4 Platform & User Info

```python
# Get user ID
user_id = event.get_user_id()

# Get bot's own ID (for @ detection)
self_id = event.get_self_id()

# Get platform
platform = event.get_platform()

# Get message origin (unique per chat)
origin = event.unified_msg_origin
```

### 7.5 LLM Access

```python
# Create an LLM request
from astrbot.api.provider import ProviderRequest

request = ProviderRequest(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
)
response = await self.context.provider_manager.text_to_text(request)
await event.reply(response.message.content)
```

### 7.6 Storage (KV Store)

```python
# Get the storage manager
storage = self.context.get_storage()

# Set a value
await storage.set("counter", 0)

# Get a value
count = await storage.get("counter", default=0)

# Delete a value
await storage.delete("counter")

# Using scope for namespacing
await storage.set("my_plugin:counter", 1, scope="global")
await storage.set("my_plugin:user_123", 5, scope="user", scope_id="123")
```

### 7.7 Other Context APIs

```python
# Get the platform message history manager
history_mgr = self.context.platform_message_history_mgr

# Get the persona manager
persona_mgr = self.context.persona_manager

# Get the database
db: BaseDatabase = self.context.database

# Get the LLM tool manager
tool_mgr = self.context.tool_manager

# Access AstrBot's event bus
event_bus = self.context.event_bus

# Register a web API endpoint
self.context.register_web_api("/my_plugin/api", handler_func, ["GET"], "Api description")
```

---

## 8. LLM/Tool Integration

Plugins can expose functions as LLM tools, allowing the AI to call plugin functionality.

### 8.1 Registering a Tool

```python
from astrbot.core.provider.func_tool_manager import FunctionTool

class MyPlugin(star.Star):
    def __init__(self, context: star.Context, config: dict | None = None):
        super().__init__(context, config)
        # Register tools on init
        self.context.tool_manager.register(MyTool(self))

class MyTool(FunctionTool):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def execute(self, **kwargs) -> str:
        """Execute the tool"""
        query = kwargs.get("query", "")
        return f"Search result for: {query}"

    def get_desc(self) -> str:
        return "Search the web for information"

    def get_params_schema(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True,
            }
        }
```

### 8.2 Tool Result to LLM

Tools can return strings or structured data that becomes part of the LLM context:

```python
async def execute(self, **kwargs) -> str | dict:
    # String result
    return "Simple result"

    # Structured result (becomes part of conversation)
    return {
        "result": "data",
        "items": ["a", "b", "c"],
    }
```

---

## 9. Plugin Pages (Dashboard Integration)

Plugins can register pages that appear in the AstrBot web dashboard.

### 9.1 Page Registration

In `metadata.yaml`:

```yaml
pages:
  - path: /my_plugin
    name: My Plugin
    icon: plugin_icon
    file: /path/to/page.html
```

### 9.2 Bridge API (Frontend → Plugin)

The dashboard page communicates with the plugin via the Bridge API:

```javascript
// In your page.html
const bridge = window.AstrBotBridge;

// Call plugin handler
const result = await bridge.call("my_plugin.get_stats", { key: "value" });

// Listen for plugin events
bridge.on("my_plugin.update", (data) => {
    console.log("Update received:", data);
});
```

### 9.3 Plugin Handler for Bridge API

```python
async def handle_web_request(self, path: str, data: dict) -> dict:
    if path == "get_stats":
        return {"users": 42, "active": True}
    raise ValueError(f"Unknown path: {path}")
```

---

## 10. Internationalization (i18n)

Plugins can provide translations for multiple languages.

### 10.1 Translation Files

Create `i18n/` directory in your plugin:

```
my_plugin/
├── i18n/
│   ├── en.json
│   ├── zh.json
│   └── ja.json
└── main.py
```

### 10.2 Translation File Format

**en.json:**
```json
{
    "greeting": "Hello, {name}!",
    "farewell": "Goodbye!",
    "items_count": "You have {count} items"
}
```

**zh.json:**
```json
{
    "greeting": "你好，{name}！",
    "farewell": "再见！",
    "items_count": "你有 {count} 个物品"
}
```

### 10.3 Using Translations in Code

```python
# In your plugin code
from astrbot.core.config.i18n_utils import _

# Get translated string (uses user's locale automatically)
greeting = _("greeting", name="Alice")

# In metadata.yaml inline i18n
i18n:
  en:
    desc: "Hello World Plugin"
  zh:
    desc: "你好世界插件"
```

### 10.4 Dashboard i18n

The dashboard's i18n system supports dynamic injection from plugins:

```javascript
// In your page.html
const i18n = window.AstrBotI18n.get();
const greeting = i18n.t("plugin_my_plugin.greeting", { name: "Alice" });
```

---

## 11. Plugin Lifecycle

### 11.1 Initialization

```python
class MyPlugin(star.Star):
    async def initialize(self) -> None:
        """Called when the plugin is activated"""
        # Setup code: open connections, load data, register handlers
        await self._load_data()
        self.context.logger.info("MyPlugin initialized!")
```

### 11.2 Termination

```python
    async def terminate(self) -> None:
        """Called when the plugin is deactivated or reloaded"""
        # Cleanup code: close connections, save state
        await self._save_data()
        self.context.logger.info("MyPlugin terminated!")
```

### 11.3 Full Lifecycle Order

```
Plugin Load:
  1. Star.__init__(context, config)
  2. metadata.yaml read
  3. @register decorators scan
  4. Star.initialize()
  5. Handlers registered in star_handlers_registry

Plugin Unload/Reload:
  1. Star.terminate()
  2. Handlers removed from star_handlers_registry
```

---

## 12. Complete Example: Hello World

### Directory Structure

```
hello_world/
├── __init__.py
├── main.py
└── metadata.yaml
```

### metadata.yaml

```yaml
name: hello_world
desc: A simple hello world plugin demonstrating the plugin API
author: Developer
version: 1.0.0
astrbot_version: ">=4.0.0"
```

### main.py

```python
"""
Hello World Plugin for AstrBot

Demonstrates:
- Basic command handler
- Event message handler
- Config access
- i18n
"""

from astrbot.api import star, register
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain


class HelloWorld(star.Star):
    """Hello World plugin demonstrating AstrBot plugin development"""

    def __init__(self, context: star.Context, config: dict | None = None):
        super().__init__(context, config)
        self.context.logger.info("HelloWorld plugin loaded!")

    async def initialize(self) -> None:
        """Called when plugin is activated"""
        self.context.logger.info("HelloWorld initializing...")

    async def terminate(self) -> None:
        """Called when plugin is deactivated"""
        self.context.logger.info("HelloWorld terminating...")

    # ─── Command Handlers ───────────────────────────────────────────────

    @register.register_command("hello")
    async def cmd_hello(self, event: AstrMessageEvent):
        """Say hello to the user
        
        Usage: @bot hello [name]
        If name is omitted, defaults to "World"
        """
        message = event.get_message_str().strip()
        if message == "hello":
            name = "World"
        else:
            # Extract name after "hello "
            name = message[len("hello "):].strip() or "World"

        await event.reply(f"Hello, {name}! 👋")

    @register.register_command("hello multilang", alias={"hi"})
    async def cmd_hello_multilang(self, event: AstrMessageEvent):
        """Say hello in the user's language"""
        from astrbot.core.config.i18n_utils import _
        
        user_lang = self.context.get_config().get("language", "en")
        greeting = _("hello_greeting", default="Hello!")
        
        await event.reply(greeting)

    @register.register_command("user add")
    async def cmd_add_user(self, event: AstrMessageEvent, name: str):
        """Add a user to the system
        
        Usage: /user add <name>
        """
        # Store in KV store
        storage = self.context.get_storage()
        users = await storage.get("users", default=[])
        users.append(name)
        await storage.set("users", users)
        
        await event.reply(f"✅ User '{name}' added! Total users: {len(users)}")

    @register.register_command("user list")
    async def cmd_list_users(self, event: AstrMessageEvent):
        """List all users"""
        storage = self.context.get_storage()
        users = await storage.get("users", default=[])
        
        if not users:
            await event.reply("📋 No users yet. Use /user add <name> to add one!")
        else:
            user_list = "\n".join(f"  • {name}" for name in users)
            await event.reply(f"📋 Users ({len(users)}):\n{user_list}")

    @register.register_command("user count")
    async def cmd_user_count(self, event: AstrMessageEvent):
        """Get the total user count"""
        storage = self.context.get_storage()
        users = await storage.get("users", default=[])
        await event.reply(f"👥 Total users: {len(users)}")

    # ─── Event Handlers ─────────────────────────────────────────────────

    @filter.event_message_type(filter.EventMessageType.TEXT)
    @register.register_regex(r"^goodbye(?:\s+(.+))?$")
    async def handle_goodbye(self, event: AstrMessageEvent):
        """Responds to 'goodbye' or 'goodbye <name>'"""
        message = event.get_message_str()
        name = message.replace("goodbye", "").strip() or "World"
        await event.reply(f"Goodbye, {name}! 👋")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_mention(self, event: AstrMessageEvent):
        """Handle @mentions when no command matches"""
        from astrbot.api.message_components import At
        
        messages = event.get_messages()
        if any(isinstance(m, At) and str(m.qq) == str(event.get_self_id()) for m in messages):
            # Bot was mentioned but no command matched
            pass  # Do nothing, let other handlers process

    # ─── LLM Hooks ──────────────────────────────────────────────────────

    @register.register_on_llm_response()
    async def on_llm_response(self, event: AstrMessageEvent, response):
        """Log LLM responses for debugging"""
        self.context.logger.debug(f"LLM response: {response.message.content[:100]}...")
```

---

## 13. Plugin Loading & Management

### 13.1 Plugin Search Paths

| Environment | Path |
|-------------|------|
| Production | `data/stars/` |
| Development | `stars/` (relative to project root) |
| Config | `data/stars_path` in `config.yaml` |

### 13.2 Plugin Manager API

```python
# In a handler or external code
from astrbot.core.star.star_manager import StarManager

star_manager: StarManager = context.star_manager

# Load a plugin
await star_manager.load_star("plugin_name")

# Unload a plugin
await star_manager.unload_star("plugin_name")

# Reload a plugin
await star_manager.reload_star("plugin_name")

# Get plugin metadata
metadata = star_manager.get_star_metadata("plugin_name")

# List all loaded plugins
plugins = star_manager.get_all_stars()
```

### 13.3 Plugin Dependencies

If your plugin requires external packages, create `requirements.txt`:

```
requests>=2.28.0
Pillow>=9.0.0
```

AstrBot will prompt to install them on plugin load.

### 13.4 Reserved Plugins

System plugins are marked as `reserved=True` and cannot be disabled:

```python
# In star_manager.py
if metadata.reserved:
    raise ValueError("Cannot disable reserved plugin")
```

---

## 14. Filter Reference

### Available Filters

| Filter | Decorator | Purpose |
|--------|-----------|---------|
| `CommandFilter` | `@register.register_command` | Match command name with parameters |
| `CommandGroupFilter` | `@register.register_command_group` | Group commands with sub-commands |
| `RegexFilter` | `@register.register_regex` | Match regex pattern |
| `PermissionTypeFilter` | `@filter.permission()` | Check user permission level |
| `EventMessageTypeFilter` | `@filter.event_message_type()` | Match message type (TEXT/IMAGE/etc.) |
| `PlatformAdapterTypeFilter` | `@filter.platform_adapter_type()` | Match specific platform (QQ/Telegram/etc.) |
| `CustomFilter` | `@register.register_custom_filter` | Custom filter logic |

### All `@filter.*` Decorators

```python
from astrbot.api.event import filter

@filter.event_message_type(event_message_type, *, priority=0)
@filter.permission(permission_type, *, raise_error=True)
@filter.platform_adapter_type(platform_type)
```

### All `@register.*` Decorators

```python
from astrbot.api import register

# Message handlers
@register.register_command(name, sub_command=None, alias=None, **kwargs)
@register.register_command_group(name, sub_command=None, alias=None, **kwargs)
@register.register_regex(pattern, **kwargs)
@register.register_custom_filter(filter_instance, raise_error=True, **kwargs)

# Event hooks
@register.register_on_astrbot_loaded()
@register.register_on_platform_loaded()
@register.register_on_plugin_loaded()
@register.register_on_plugin_unloaded()
@register.register_on_plugin_error()
@register.register_on_llm_request()
@register.register_on_llm_response()
@register.register_on_waiting_llm_request()
@register.register_on_agent_begin()
@register.register_on_agent_done()
@register.register_on_decorating_result()
@register.register_on_calling_func_tool()
@register.register_on_using_llm_tool()
@register.register_on_llm_tool_respond()
@register.register_after_message_sent()

# LLM tools
@register.register_llm_tool(name, desc=None, **kwargs)
```

---

## 15. Event Type Reference

| EventType | Description | Triggered When |
|-----------|-------------|----------------|
| `OnAstrBotLoadedEvent` | AstrBot startup complete | Bot process starts |
| `OnPlatformLoadedEvent` | Platform adapter loaded | Each platform (QQ/Telegram/etc.) initializes |
| `AdapterMessageEvent` | Incoming platform message | User sends any message |
| `OnWaitingLLMRequestEvent` | Before LLM lock acquisition | Waiting to call LLM (notification only) |
| `OnLLMRequestEvent` | LLM about to be called | LLM request initiated |
| `OnLLMResponseEvent` | LLM response received | LLM returns a response |
| `OnAgentBeginEvent` | Agent execution starts | Agent begins running |
| `OnAgentDoneEvent` | Agent execution completes | Agent finishes |
| `OnDecoratingResultEvent` | Message about to be sent | Pre-send formatting |
| `OnCallingFuncToolEvent` | Tool function called | LLM requests tool execution |
| `OnUsingLLMToolEvent` | LLM tool invoked | Tool starts executing |
| `OnLLMToolRespondEvent` | Tool execution returns | Tool completes |
| `OnAfterMessageSentEvent` | Message sent | After bot sends a message |
| `OnPluginErrorEvent` | Plugin throws exception | Any unhandled plugin error |
| `OnPluginLoadedEvent` | Plugin finishes loading | Plugin activation complete |
| `OnPluginUnloadedEvent` | Plugin unloaded | Plugin deactivation complete |

---

## Appendix: Built-in Plugin Example

The internal `astrbot` plugin (in `astrbot/builtin_stars/astrbot/`) is the reference implementation:

```
astrbot/builtin_stars/astrbot/
├── __init__.py
├── main.py              # Main Star class with commands
├── metadata.yaml        # name: astrbot, version: 4.1.0
└── long_term_memory.py  # Additional module
```

Key patterns from `main.py`:

```python
class Main(star.Star):
    @filter.event_message_type(filter.EventMessageType.ALL, priority=maxsize)
    async def handle_session_control_agent(self, event: AstrMessageEvent):
        """Highest priority handler for session control"""
        ...

    @filter.event_message_type(filter.EventMessageType.ALL, priority=maxsize - 1)
    async def handle_empty_mention(self, event: AstrMessageEvent):
        """Handle @bot with no command — wait for next message"""
        ...

    @register.register_command("clear")
    async def cmd_clear(self, event: AstrMessageEvent):
        """Clear conversation history"""
        ...
```

---

## Appendix: Common Patterns

### Pattern: Rate Limiting

```python
import time
from collections import defaultdict

class MyPlugin(star.Star):
    def __init__(self, context, config):
        super().__init__(context, config)
        self._rate_limits = defaultdict(list)

    def _check_rate_limit(self, user_id: str, max_calls: int = 5, window: int = 60) -> bool:
        now = time.time()
        self._rate_limits[user_id] = [
            t for t in self._rate_limits[user_id] if now - t < window
        ]
        if len(self._rate_limits[user_id]) >= max_calls:
            return False
        self._rate_limits[user_id].append(now)
        return True
```

### Pattern: User State Machine

```python
class MyPlugin(star.Star):
    # State storage: user_id -> state name
    _user_states: dict[str, str] = {}

    @register.register_command("step1")
    async def cmd_step1(self, event: AstrMessageEvent):
        user_id = event.get_user_id()
        self._user_states[user_id] = "step1"
        await event.reply("Step 1 complete. Now say 'next' to continue.")

    @register.register_regex(r"^next$")
    async def handle_next(self, event: AstrMessageEvent):
        user_id = event.get_user_id()
        state = self._user_states.get(user_id)
        if state == "step1":
            await event.reply("Proceeding to step 2...")
```

### Pattern: Async Background Task

```python
import asyncio

class MyPlugin(star.Star):
    def __init__(self, context, config):
        super().__init__(context, config)
        self._background_tasks: list[asyncio.Task] = []

    async def initialize(self):
        task = asyncio.create_task(self._background_loop())
        self._background_tasks.append(task)

    async def terminate(self):
        for task in self._background_tasks:
            task.cancel()

    async def _background_loop(self):
        while True:
            await asyncio.sleep(60)
            # Do periodic work
```

---

*Document version: 1.0 — Based on AstrBot v4.x*
*Generated from source analysis of `astrbot/core/star/` and `astrbot/builtin_stars/astrbot/`*
