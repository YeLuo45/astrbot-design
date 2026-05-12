# 平台适配器架构分析

## 概述

AstrBot 通过插件形式集成平台适配器，支持连接任意 IM 平台（Lark、钉钉、Minecraft 等）。平台适配器将各平台差异化的消息格式统一转换为 AstrBot 内部标准格式，实现"一条核心逻辑，多端无缝接入"。

## 架构分层

```
┌──────────────────────────────────────────┐
│           AstrBot 核心（与平台无关）         │
├──────────────────────────────────────────┤
│  平台适配器层（Platform Adapter）            │
│  ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ QQ     │ │ Lark   │ │ 自定义  │        │
│  └────────┘ └────────┘ └────────┘        │
├──────────────────────────────────────────┤
│  各平台 SDK / API / WebSocket            │
└──────────────────────────────────────────┘
```

## 核心组件

### Platform（平台适配器基类）

`Platform` 是所有平台适配器的基类，负责：

- 管理平台连接生命周期
- 接收平台消息并转换为 `AstrBotMessage`
- 提供消息发送能力

关键方法：

| 方法 | 职责 |
|------|------|
| `send_by_session()` | 通过会话发送消息链 |
| `convert_message()` | 将平台原生消息转为 AstrBot 标准格式 |
| `meta()` | 返回平台元数据（名称、描述） |

### AstrBotMessage（标准消息格式）

平台消息统一转换为以下字段：

| 字段 | 说明 | 重要性 |
|------|------|--------|
| `type` | 消息类型：群组/私聊 | 必填 |
| `group_id` | 群组 ID（私聊可省略） | 群消息必填 |
| `message_str` | 纯文本消息内容 | 必填 |
| `sender` | 发送者信息（user_id, nickname） | 必填 |
| `message` | 消息链（Plain、Image 等组件） | 必填 |
| `session_id` | 会话 ID | 必填 |
| `message_id` | 平台消息 ID | 选填 |
| `raw_message` | 原始平台消息 | 选填 |

### MessageChain（消息链）

AstrBot 采用消息链模式处理多媒体消息，每条消息由多个组件构成：

```python
message_chain = [
    Plain(text="Hello"),      # 文本
    Image(file="/path/img.png"),  # 图片
    Record(file="/path/audio"),   # 语音
]
```

### AstrMessageEvent（平台事件）

继承自 `AstrMessageEvent`，封装平台特定上下文：

- 持有平台 SDK Client 引用（用于回复）
- 实现 `send()` 方法将消息链发回平台
- 提供 `get_sender_id()` 获取发送者 ID

## 开发流程

### 1. 创建平台客户端

```python
class FakeClient:
    async def start_polling(self):
        # 监听消息，回调 on_message_received

    async def send_text(self, to: str, message: str):
        # 发送文本消息

    async def send_image(self, to: str, image_path: str):
        # 发送图片
```

### 2. 实现 Platform 适配器类

```python
@register_platform_adapter("fake", "fake adapter", default_config_tmpl={
    "token": "***",
    "username": "bot_username"
})
class FakePlatformAdapter(Platform):
    async def initialize(self):
        # 初始化客户端，设置消息回调

    async def convert_message(self, data: dict) -> AstrBotMessage:
        # 平台消息 → AstrBotMessage
        return abm

    def meta(self) -> PlatformMetadata:
        return PlatformMetadata("fake", "fake adapter")
```

### 3. 实现 PlatformEvent

```python
class FakePlatformEvent(AstrMessageEvent):
    async def send(self, message: MessageChain):
        for component in message.chain:
            if isinstance(component, Plain):
                await self.client.send_text(...)
            elif isinstance(component, Image):
                await self.client.send_image(...)
```

### 4. 注册适配器

在插件初始化时 import 适配器模块，装饰器自动完成注册：

```python
class MyPlugin(Star):
    def __init__(self, context: Context):
        from .fake_platform_adapter import FakePlatformAdapter  # noqa
```

## 消息类型

| 类型 | 常量 | 说明 |
|------|------|------|
| 群组消息 | `GROUP_MESSAGE` | 群内成员发送 |
| 私聊消息 | `FRIEND_MESSAGE` | 好友私聊 |

## 已支持平台一览

| 平台 | 协议 | 备注 |
|------|------|------|
| QQ (官方) | WebSocket / Webhook | NT QQ |
| QQ (Old) | OneBot v11 | 兼容旧版 |
| Discord | WebSocket | - |
| Telegram | Bot API | - |
| Lark | WebSocket | - |
| DingTalk | Webhook | - |
| KOOK | WebSocket | - |
| WeChat (公众号) | Webhook | - |
| WeChat (企业) | Webhook | - |
| Slack | WebSocket | - |
| Satori | 统一协议 | 平台无关 |

## 设计价值

- **插件化**：无需修改核心代码即可新增平台支持
- **统一抽象**：上层业务逻辑与平台无关
- **标准化**：AstrBotMessage 统一所有平台消息格式
- **可测试**：Platform 接口便于单元测试
