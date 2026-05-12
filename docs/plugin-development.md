---
outline: deep
---

# AstrBot 插件开发指南

欢迎来到 AstrBot 插件开发指南！本指南将引导您完成插件开发的完整流程。

## 目录

- [环境准备](#环境准备)
- [开发原则](#开发原则)
- [最小实例](#最小实例)
- [消息事件处理](#消息事件处理)
- [消息发送](#消息发送)
- [插件配置](#插件配置)
- [插件国际化](#插件国际化)
- [插件页面 (Pages)](#插件页面-pages)
- [AI 与 LLM 调用](#ai-与-llm-调用)
- [函数工具](#函数工具)
- [会话控制](#会话控制)
- [文转图](#文转图)
- [事件钩子](#事件钩子)
- [其他功能](#其他功能)
- [发布插件](#发布插件)

---

## 环境准备

### 获取插件模板

1. 打开 AstrBot 插件模板: [helloworld](https://github.com/Soulter/helloworld)
2. 点击右上角的 `Use this template`
3. 点击 `Create new repository`
4. 填写插件名（推荐以 `astrbot_plugin_` 开头，全部小写，不能包含空格）

### 克隆项目到本地

```bash
git clone https://github.com/AstrBotDevs/AstrBot
mkdir -p AstrBot/data/plugins
cd AstrBot/data/plugins
git clone 插件仓库地址
```

### 更新 metadata.yaml

编辑插件目录下的 `metadata.yaml` 文件，填写插件元数据信息。这是 AstrBot 识别插件的必要文件。

### 设置插件 Logo（可选）

在插件目录下添加 `logo.png` 文件作为插件 Logo。长宽比 1:1，推荐尺寸 256x256。

### 声明支持平台（可选）

在 `metadata.yaml` 中添加 `support_platforms` 字段：

```yaml
support_platforms:
  - telegram
  - discord
```

支持的平台：`aiocqhttp`、`qq_official`、`telegram`、`wecom`、`lark`、`dingtalk`、`discord`、`slack`、`kook`、`vocechat`、`weixin_official_account`、`satori`、`misskey`、`line`

### 声明 AstrBot 版本范围（可选）

```yaml
astrbot_version: ">=4.16,<5"
```

### 调试插件

AstrBot 采用运行时注入插件机制。启动 AstrBot 本体后，修改插件代码可在 WebUI 插件管理处点击 `重载插件` 热更新。

### 插件依赖管理

在插件目录下创建 `requirements.txt` 文件写入第三方依赖，避免用户安装时出现 Module Not Found 问题。

---

## 开发原则

开发插件请遵守以下原则：

- 功能需经过测试
- 需包含良好的注释
- 持久化数据请存储于 `data` 目录下，防止更新/重装插件时数据被覆盖
- 良好的错误处理机制，不要让插件因一个错误而崩溃
- 提交前使用 [ruff](https://docs.astral.sh/ruff/) 工具格式化代码
- 不要使用 `requests` 库进行网络请求，使用 `aiohttp`、`httpx` 等异步库
- 对某个插件进行功能扩增时，优先提交 PR

---

## 最小实例

```python
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger

class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是 hello world 指令'''
        user_name = event.get_sender_name()
        yield event.plain_result(f"Hello, {user_name}!")

    async def terminate(self):
        '''插件卸载/停用时调用'''
```

关键点：
1. 插件继承自 `Star` 基类
2. `__init__` 方法接收 `Context` 对象
3. Handler 必须在插件类中定义，前两个参数为 `self` 和 `event`
4. 使用 `from astrbot.api import logger` 获取日志对象
5. 插件类所在文件名必须命名为 `main.py`

---

## 消息事件处理

### 指令

```python
@filter.command("helloworld")
async def helloworld(self, event: AstrMessageEvent):
    yield event.plain_result("Hello!")
```

### 带参指令

```python
@filter.command("echo")
async def echo(self, event: AstrMessageEvent, message: str):
    yield event.plain_result(f"你发了: {message}")

@filter.command("add")
async def add(self, event: AstrMessageEvent, a: int, b: int):
    yield event.plain_result(f"结果是: {a + b}")
```

### 指令组

```python
@filter.command_group("math")
def math():
    pass

@math.command("add")
async def add(self, event: AstrMessageEvent, a: int, b: int):
    yield event.plain_result(f"结果是: {a + b}")

@math.command("sub")
async def sub(self, event: AstrMessageEvent, a: int, b: int):
    yield event.plain_result(f"结果是: {a - b}")
```

### 事件类型过滤

```python
# 私聊消息
@filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
async def on_private(self, event: AstrMessageEvent):
    yield event.plain_result("收到私聊！")

# 群聊消息
@filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)

# 所有消息
@filter.event_message_type(filter.EventMessageType.ALL)
```

### 平台过滤

```python
@filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP | filter.PlatformAdapterType.QQOFFICIAL)
async def on_aiocqhttp(self, event: AstrMessageEvent):
    yield event.plain_result("收到 QQ 消息！")
```

### 管理员指令

```python
@filter.permission_type(filter.PermissionType.ADMIN)
@filter.command("admin_cmd")
async def admin_cmd(self, event: AstrMessageEvent):
    pass
```

### 多个过滤器

```python
@filter.command("helloworld")
@filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
async def helloworld(self, event: AstrMessageEvent):
    yield event.plain_result("你好！")
```

### 优先级

```python
@filter.command("helloworld", priority=1)
async def helloworld(self, event: AstrMessageEvent):
    yield event.plain_result("Hello!")
```

---

## 消息发送

### 被动消息

```python
yield event.plain_result("Hello!")
yield event.image_result("path/to/image.jpg")
yield event.image_result("https://example.com/image.jpg")
```

### 主动消息

```python
from astrbot.api.event import MessageChain

@filter.command("helloworld")
async def helloworld(self, event: AstrMessageEvent):
    message_chain = MessageChain().message("Hello!").file_image("path/to/image.jpg")
    await self.context.send_message(event.unified_msg_origin, message_chain)
```

### 富媒体消息

```python
import astrbot.api.message_components as Comp

chain = [
    Comp.At(qq=event.get_sender_id()),
    Comp.Plain("来看这个图："),
    Comp.Image.fromURL("https://example.com/image.jpg"),
    Comp.Image.fromFileSystem("path/to/image.jpg"),
]
yield event.chain_result(chain)
```

常用消息组件：
- `Comp.Plain(text)` - 文本消息
- `Comp.At(qq=123456)` - At 用户
- `Comp.Image.fromURL(url)` / `Comp.Image.fromFileSystem(path)` - 图片
- `Comp.File(file, name)` - 文件
- `Comp.Record(file, url)` - 语音
- `Comp.Video.fromURL(url)` / `Comp.Video.fromFileSystem(path)` - 视频
- `Comp.Face(id)` - QQ 表情

### 发送群合并转发消息

```python
from astrbot.api.message_components import Node, Plain, Image

node = Node(
    uin=905617992,
    name="Soulter",
    content=[Plain("hi"), Image.fromFileSystem("test.jpg")]
)
yield event.chain_result([node])
```

### 控制事件传播

```python
@filter.command("check")
async def check(self, event: AstrMessageEvent):
    if not some_condition:
        yield event.plain_result("检查失败")
        event.stop_event()  # 停止事件传播
```

---

## 插件配置

### 定义配置 Schema

在插件目录下创建 `_conf_schema.json`：

```json
{
  "token": {
    "description": "Bot Token",
    "type": "string"
  },
  "enable": {
    "description": "是否启用",
    "type": "bool",
    "default": true
  },
  "sub_config": {
    "description": "嵌套配置",
    "type": "object",
    "items": {
      "name": {
        "description": "名称",
        "type": "string"
      }
    }
  }
}
```

配置类型支持：`string`、`text`、`int`、`float`、`bool`、`object`、`list`、`dict`、`template_list`、`file`

### 在插件中使用配置

```python
from astrbot.api import AstrBotConfig

class ConfigPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        print(self.config["token"])
        # self.config.save_config() # 保存配置
```

### _special 字段

`_special` 字段用于调用 AstrBot 提供的可视化选取功能：

- `select_provider` - 模型提供商选取
- `select_provider_tts` - TTS 提供商选取
- `select_provider_stt` - STT 提供商选取
- `select_persona` - 人格选取
- `select_knowledgebase` - 知识库选取

---

## 插件国际化

插件可以在 `.astrbot-plugin/i18n/` 目录下提供语言文件：

```
your_plugin/
  metadata.yaml
  _conf_schema.json
  .astrbot-plugin/
    i18n/
      zh-CN.json
      en-US.json
```

### 元数据翻译

```json
{
  "metadata": {
    "display_name": "天气助手",
    "short_desc": "一句话天气查询。",
    "desc": "查询天气并提供出行建议。"
  }
}
```

### 配置项翻译

```json
{
  "config": {
    "enable": {
      "description": "启用",
      "hint": "是否启用这个插件。"
    }
  }
}
```

---

## 插件页面 (Pages)

插件可以通过 `pages/` 目录暴露 Dashboard 页面。

### 目录结构

```
your_plugin/
  main.py
  pages/
    settings/
      index.html
    dashboard/
      index.html
      app.js
      style.css
```

### 前端示例

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>Plugin Page Demo</title>
  </head>
  <body>
    <button id="ping">Ping</button>
    <pre id="output"></pre>
    <script type="module" src="./app.js"></script>
  </body>
</html>
```

```js
const bridge = window.AstrBotPluginPage;
const output = document.getElementById("output");

const context = await bridge.ready();
output.textContent = JSON.stringify(context, null, 2);

document.getElementById("ping").addEventListener("click", async () => {
  const result = await bridge.apiGet("ping");
  output.textContent = JSON.stringify(result, null, 2);
});
```

### 注册后端 API

```python
from quart import jsonify
from astrbot.api.star import Context, Star

PLUGIN_NAME = "your_plugin"

class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        context.register_web_api(
            f"/{PLUGIN_NAME}/ping",
            self.page_ping,
            ["GET"],
            "Page ping",
        )

    async def page_ping(self):
        return jsonify({"message": "pong"})
```

### Bridge API

- `ready()` - 等待 bridge 就绪
- `getContext()` - 获取当前上下文
- `getLocale()` - 获取当前语言
- `getI18n()` - 获取 i18n 资源
- `t(key, fallback)` - 翻译文案
- `onContext(handler)` - 监听上下文变化
- `apiGet(endpoint, params)` - GET 请求
- `apiPost(endpoint, body)` - POST 请求
- `upload(endpoint, file)` - 文件上传
- `download(endpoint, params, filename)` - 文件下载
- `subscribeSSE(endpoint, handlers, params)` - SSE 订阅
- `unsubscribeSSE(subscriptionId)` - 取消 SSE 订阅

---

## AI 与 LLM 调用

### 获取提供商

```python
# 获取当前使用的提供商
prov = self.context.get_using_provider(umo=event.unified_msg_origin)

# 根据 ID 获取
prov = self.context.get_provider_by_id(provider_id="xxxx")

# 获取所有提供商
all_provs = self.context.get_all_providers()
```

### 调用 LLM

```python
llm_resp = await prov.text_chat(
    prompt="Hi!",
    context=[
        {"role": "user", "content": "balabala"},
        {"role": "assistant", "content": "response balabala"}
    ],
    system_prompt="You are a helpful assistant."
)
```

### 获取其他类型提供商

```python
# 语音识别
stt = self.context.get_using_stt_provider(umo=event.unified_msg_origin)
all_stt = self.context.get_all_stt_providers()

# 语音合成
tts = self.context.get_using_tts_provider(umo=event.unified_msg_origin)
all_tts = self.context.get_all_tts_providers()

# 嵌入
all_embedding = self.context.get_all_embedding_providers()
```

### 对话管理器

```python
conv_mgr = self.context.conversation_manager
curr_cid = await conv_mgr.get_curr_conversation_id(uid)
conversation = await conv_mgr.get_conversation(uid, curr_cid)
```

### 人格管理器

```python
persona_mgr = self.context.persona_manager
personas = persona_mgr.get_all_personas()
persona = persona_mgr.get_persona(persona_id)
```

---

## 函数工具

### 以类的形式定义（推荐）

```python
from astrbot.api import FunctionTool
from dataclasses import dataclass, field

@dataclass
class HelloWorldTool(FunctionTool):
    name: str = "hello_world"
    description: str = "Say hello to the world."
    parameters: dict = field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "greeting": {
                "type": "string",
                "description": "The greeting message.",
            },
        },
        "required": ["greeting"],
    })

    async def run(self, event: AstrMessageEvent, greeting: str):
        return f"{greeting}, World!"
```

注册工具：

```python
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.context.add_llm_tools(HelloWorldTool())
```

### 以装饰器形式定义

```python
@filter.llm_tool(name="get_weather")
async def get_weather(self, event: AstrMessageEvent, location: str) -> MessageEventResult:
    '''获取天气信息。

    Args:
        location(string): 地点
    '''
    yield event.plain_result("天气信息: " + resp)
```

---

## 会话控制

会话控制用于需要多轮对话的场景，如成语接龙、游戏等。

```python
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@filter.command("成语接龙")
async def handle_idiom(self, event: AstrMessageEvent):
    yield event.plain_result("请发送一个成语~")

    @session_waiter(timeout=60, record_history_chains=False)
    async def idiom_waiter(controller: SessionController, event: AstrMessageEvent):
        idiom = event.message_str

        if idiom == "退出":
            await event.send(event.plain_result("已退出~"))
            controller.stop()
            return

        await event.send(event.plain_result(f"你说了: {idiom}"))
        controller.keep(timeout=60, reset_timeout=True)

    try:
        await idiom_waiter(event)
    except TimeoutError:
        yield event.plain_result("你超时了！")
```

### SessionController 方法

- `keep(timeout, reset_timeout)` - 保持会话，重置超时时间
- `stop()` - 结束会话
- `get_history_chains()` - 获取历史消息链

### 自定义会话 ID 算子

```python
from astrbot.core.utils.session_waiter import SessionFilter

class GroupFilter(SessionFilter):
    def filter(self, event: AstrMessageEvent) -> str:
        return event.get_group_id() if event.get_group_id() else event.unified_msg_origin

await idiom_waiter(event, session_filter=GroupFilter())
```

---

## 文转图

### 基本用法

```python
@filter.command("image")
async def render_image(self, event: AstrMessageEvent, text: str):
    url = await self.text_to_image(text)
    yield event.image_result(url)
```

### 自定义 HTML 模板

```python
TMPL = '''
<div style="font-size: 32px;">
<h1 style="color: black">Todo List</h1>
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
</div>
'''

@filter.command("todo")
async def custom_t2i(self, event: AstrMessageEvent):
    url = await self.html_render(TMPL, {"items": ["吃饭", "睡觉", "玩原神"]})
    yield event.image_result(url)
```

---

## 事件钩子

### Bot 初始化完成

```python
@filter.on_astrbot_loaded()
async def on_loaded(self):
    print("AstrBot 初始化完成")
```

### LLM 请求时

```python
from astrbot.api.provider import ProviderRequest

@filter.on_llm_request()
async def on_request(self, event: AstrMessageEvent, req: ProviderRequest):
    req.system_prompt += "自定义 system_prompt"
```

### LLM 请求完成时

```python
from astrbot.api.provider import LLMResponse

@filter.on_llm_response()
async def on_response(self, event: AstrMessageEvent, resp: LLMResponse):
    print(resp)
```

### 发送消息前

```python
@filter.on_decorating_result()
async def on_decorating(self, event: AstrMessageEvent):
    result = event.get_result()
    chain = result.chain
    chain.append(Comp.Plain("!"))
```

### 发送消息后

```python
@filter.after_message_sent()
async def after_sent(self, event: AstrMessageEvent):
    pass
```

### Agent 钩子 (v4.23.1+)

```python
# Agent 开始运行时
@filter.on_agent_begin()
async def on_begin(self, event: AstrMessageEvent, run_context):
    print("Agent 开始运行")

# LLM 工具调用前
@filter.on_using_llm_tool()
async def on_tool_call(self, event: AstrMessageEvent, tool, tool_args):
    print(tool.name, tool_args)

# Agent 运行完成时
@filter.on_agent_done()
async def on_done(self, event: AstrMessageEvent, run_context, resp):
    print(resp)
```

---

## 其他功能

### 获取消息平台实例

```python
from astrbot.api.event import filter
from astrbot.api.platform import AiocqhttpAdapter

platform = self.context.get_platform(filter.PlatformAdapterType.AIOCQHTTP)
```

### 调用 QQ 协议端 API

```python
if event.get_platform_name() == "aiocqhttp":
    from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
    assert isinstance(event, AiocqhttpMessageEvent)
    client = event.bot
    payloads = {"message_id": event.message_obj.message_id}
    ret = await client.api.call_action('delete_msg', **payloads)
```

### 注册异步任务

```python
import asyncio

class TaskPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        asyncio.create_task(self.my_task())

    async def my_task(self):
        await asyncio.sleep(1)
        print("Hello")
```

### 获取所有插件

```python
plugins = self.context.get_all_stars()
```

### 获取所有平台

```python
from astrbot.api.platform import Platform
platforms = self.context.platform_manager.get_insts()
```

---

## 发布插件

### 准备发布

1. 确保插件压缩包（zip）大小不超过 **16MB**
2. 压缩图片等静态资源
3. 清理不必要的文件（`.git`、`__pycache__`、`node_modules` 等）
4. 在仓库根目录添加 `.gitignore`

### 提交到插件市场

1. 前往 [AstrBot 插件市场](https://plugins.astrbot.app)
2. 点击右下角 `+` 按钮
3. 填写基本信息、作者信息、仓库信息
4. 点击 `提交到 GITHUB` 按钮
5. 在 GitHub Issue 页面确认信息后点击 `Create`

---

## 平台适配矩阵

| 平台 | At | Plain | Image | Record | Video | Reply | 主动消息 |
|------|----|----|----|----|----|----|----|
| QQ 个人号 (aiocqhttp) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Telegram | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| QQ 官方接口 | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 飞书 | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| 企业微信 | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| 钉钉 | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

> [!NOTE]
> QQ 个人号 (aiocqhttp) 支持所有消息类型，包括戳一戳、合并转发等。钉钉图片仅支持 HTTP 链接。

---

## 相关资源

- [新插件开发指南](./zh/dev/star/plugin-new.md)
- [旧插件开发指南](./zh/dev/star/plugin.md)
- [插件配置](./zh/dev/star/guides/plugin-config.md)
- [插件国际化](./zh/dev/star/guides/plugin-i18n.md)
- [插件页面](./zh/dev/star/guides/plugin-pages.md)
- [发布插件](./zh/dev/star/plugin-publish.md)
- [开发者 QQ 群](./zh/dev/star/plugin-new.md): `975206796`
