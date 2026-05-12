# AstrBot HTTP API 分析

## 1. 概述

AstrBot 从 v4.18.0 开始提供基于 API Key 的 HTTP API，允许开发者通过标准 HTTP 请求访问核心能力。

**基础 URL**: `/api/v1`

**认证方式**:
```http
Authorization: Bearer <api_key>
# 或
X-API-Key: <api_key>
```

## 2. API Key 与 Scope 权限

创建 API Key 时可配置 scopes，每个 scope 控制可访问的接口范围：

| Scope | 作用 | 可访问接口 |
|-------|------|-----------|
| `chat` | 调用对话能力、查询对话会话 | `POST /api/v1/chat`、`GET /api/v1/chat/sessions` |
| `config` | 获取可用配置文件列表 | `GET /api/v1/configs` |
| `file` | 上传附件文件 | `POST /api/v1/file` |
| `im` | 主动发 IM 消息、查询 bot/platform 列表 | `POST /api/v1/im/message`、`GET /api/v1/im/bots` |

> 未包含目标接口所需 scope 时返回 `403 Insufficient API key scope`

## 3. 核心接口

### 3.1 对话接口

**发送对话消息** (SSE 流式返回)
```
POST /api/v1/chat
```

请求体：
```json
{
  "message": "Hello",           // 字符串或消息段数组
  "session_id": "uuid",         // 可选，不传则自动创建
  "username": "user123"         // 必填
}
```

**获取会话列表**
```
GET /api/v1/chat/sessions?username=user123&page=1&size=20
```

### 3.2 消息段 (Message Chain) 格式

`message` 字段支持两种格式：

**纯文本格式**:
```json
{ "message": "Hello" }
```

**消息段数组格式**:
```json
{
  "message": [
    { "type": "plain", "text": "请看这个文件" },
    { "type": "file", "attachment_id": "uuid" }
  ]
}
```

支持的 type：

| type | 必填字段 | 可选字段 | 说明 |
|------|---------|---------|------|
| `plain` | `text` | - | 文本段 |
| `reply` | `message_id` | `selected_text` | 引用回复 |
| `image` | `attachment_id` | - | 图片附件 |
| `record` | `attachment_id` | - | 音频附件 |
| `file` | `attachment_id` | - | 通用文件 |
| `video` | `attachment_id` | - | 视频附件 |

### 3.3 文件上传

```
POST /api/v1/file
```

返回 `attachment_id`，可用于消息段中。

### 3.4 IM 消息发送

**主动发消息**
```
POST /api/v1/im/message
```

**获取 bot/platform 列表**
```
GET /api/v1/im/bots
```

### 3.5 配置管理

```
GET /api/v1/configs
```

获取可用配置文件列表。

## 4. API 设计特点

### 4.1 统一认证
- API Key 通过 HTTP Header 传递
- 支持 Bearer Token 和 X-API-Key 两种形式

### 4.2 Scope 细分权限
- 最小权限原则，每个 Key 可配置多个 scope
- 接口级别权限控制

### 4.3 SSE 流式响应
- 对话接口采用 Server-Sent Events
- 支持实时流式输出

### 4.4 消息段抽象
- 统一的消息段格式支持多种内容类型
- 可扩展的 type 系统

## 5. 与 WebSocket 的对比

| 特性 | HTTP API | WebSocket |
|------|----------|-----------|
| 适用场景 | 单次请求、异步消息 | 实时双向通信 |
| 认证 | API Key | 继承 WebUI 会话 |
| 消息格式 | 消息段 | 平台特定格式 |
| 用途 | 服务端集成、跨语言调用 | 实时聊天、IM |

## 6. 使用场景

1. **第三方应用集成**: 将 AstrBot 能力嵌入到其他应用
2. **服务端推送**: 通过 IM 接口主动触达用户
3. **多平台桥接**: 统一 API 对接不同 IM 平台
4. **自动化工作流**: 结合 Cron 实现定时任务
