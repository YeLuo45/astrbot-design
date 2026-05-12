# AstrBot MCP 集成分析

## 1. 概述

MCP (Model Context Protocol) 是一种开放标准协议，用于在大模型和数据源之间建立安全双向连接。AstrBot v3.5.0+ 支持 MCP 协议，可添加多个 MCP 服务器并调用其函数工具。

**核心优势**：
- 函数工具独立部署，按需扩展
- 标准化协议，无需为每个工具单独适配
- 支持 uv/npm 两种启动方式

## 2. 架构

```
┌─────────────┐     MCP Protocol      ┌──────────────────┐
│  AstrBot    │◄──────────────────►│   MCP Server     │
│  (Client)   │                      │  (Function Tools)│
└─────────────┘                      └──────────────────┘
       ▲                                    ▲
       │                                    │
   Tool Call                           External
   Response                            Services
                                          │
                                    ┌──────┴──────┐
                                    │  Arxiv API  │
                                    │  GitHub API │
                                    │  Database   │
                                    │  Filesystem │
                                    └─────────────┘
```

## 3. 前提条件

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| `uv` | 启动 Python-based MCP 服务器 | `pip install uv` 或 WebUI 快捷安装 |
| `node` (npm) | 启动 Node.js-based MCP 服务器 | Docker 容器内需手动安装 |

### Docker 环境安装 node

```bash
docker exec -it astrbot /bin/bash
apt update && apt install curl -y
export NVM_NODEJS_ORG_MIRROR=http://nodejs.org/dist
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
. "$HOME/.nvm/nvm.sh"
nvm install 22
```

## 4. MCP 服务器配置

### 配置结构

```json
{
  "command": "uv",
  "args": [
    "tool",
    "run",
    "<mcp-server-name>",
    "--storage-path",
    "data/<storage>"
  ]
}
```

### 环境变量配置

使用 `env` 工具传递 Token 等敏感配置：

```json
{
  "command": "env",
  "args": [
    "API_TOKEN=***",
    "API_URL=https://xxx.com",
    "uv",
    "tool",
    "run",
    "xxx-mcp-server",
    "--storage-path",
    "data/res"
  ]
}
```

### 配置示例

**ArXiv 论文查询** ([arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server)):

```json
{
  "command": "uv",
  "args": ["tool", "run", "arxiv-mcp-server", "--storage-path", "data/arxiv"]
}
```

## 5. 常用 MCP 服务器

| 服务器 | 用途 | 来源 |
|--------|------|------|
| arxiv-mcp-server | ArXiv 论文查询 | GitHub |
| github-mcp-server | GitHub API 操作 | modelcontextprotocol/servers |
| filesystem-mcp | 文件系统操作 | modelcontextprotocol/servers |
| slack-mcp | Slack 消息 | modelcontextprotocol/servers |
| [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 完整列表 | GitHub |

## 6. 在 AstrBot 中使用

1. 在 WebUI → 设置 → MCP 中配置服务器
2. 启用所需的函数工具
3. 在对话中自然语言调用

## 7. 与内置 Tools 的对比

| 特性 | 内置 Tools | MCP Tools |
|------|-----------|-----------|
| 部署方式 | 内置 | 独立进程 |
| 扩展性 | 有限 | 按需添加 |
| 协议 | 内部调用 | 标准化 MCP |
| 依赖 | 随 AstrBot 安装 | 独立管理 |
| 适用场景 | 通用功能 | 第三方服务集成 |

## 8. 参考链接

- [MCP 官方文档](https://modelcontextprotocol.io/introduction)
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- [MCP.so](https://mcp.so)
