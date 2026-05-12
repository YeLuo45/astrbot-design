# AstrBot Dashboard 前端架构分析

## 1. 技术栈概览

| 类别 | 技术 | 版本 |
|------|------|------|
| 核心框架 | Vue | 3.3.4 |
| 类型系统 | TypeScript | 5.1.6 |
| 构建工具 | Vite | 6.4.1 |
| UI 框架 | Vuetify | 3.7.11 |
| 状态管理 | Pinia | 2.1.6 |
| 路由 | Vue Router | 4.2.4 |
| HTTP 客户端 | Axios | 1.13.5 |
| 国际化 | 自定义 i18n | - |

## 2. 项目目录结构

```
src/
├── assets/              # 静态资源（MDI 图标子集、图片等）
├── components/          # 可复用组件
│   ├── chat/           # 聊天相关组件
│   ├── config/         # 配置相关组件
│   ├── extension/      # 插件相关组件
│   ├── folder/         # 文件夹树通用组件（可复用）
│   ├── platform/       # 平台相关组件
│   ├── provider/       # 提供者相关组件
│   └── shared/         # 共享全局组件
├── composables/         # Vue Composition API 组合函数
│   ├── useConversations.ts
│   ├── useMessages.ts
│   ├── useSessions.ts
│   ├── useProviderModelConfigDialog.ts
│   └── ...
├── config.ts            # 前端配置常量
├── i18n/                # 国际化系统
│   ├── locales/         # 翻译文件（zh-CN, en-US, ru-RU）
│   ├── composables.ts   # i18n 组合函数
│   ├── translations.ts  # 静态翻译数据
│   ├── loader.ts
│   └── types.ts
├── layouts/             # 页面布局
│   ├── blank/          # 空白布局（用于登录页）
│   └── full/           # 完整布局（含侧边栏+头部）
│       ├── vertical-header/
│       └── vertical-sidebar/
├── plugins/             # Vuetify 插件配置
│   ├── vuetify.ts
│   └── confirmPlugin.ts
├── router/              # 路由配置
│   ├── index.ts         # 路由主体 + 守卫
│   ├── MainRoutes.ts    # 主应用路由
│   ├── AuthRoutes.ts    # 认证路由
│   └── ChatBoxRoutes.ts # 聊天窗口路由
├── scss/                # 样式文件
│   ├── layout/
│   ├── components/
│   ├── pages/
│   └── style.scss
├── stores/              # Pinia 状态管理
│   ├── auth.ts          # 认证状态
│   ├── customizer.ts    # UI 自定义设置
│   ├── personaStore.ts  # Persona 状态
│   ├── common.js        # 通用状态
│   ├── routerLoading.ts # 路由加载状态
│   └── toast.js         # Toast 通知状态
├── styles/              # 样式
├── theme/               # Vuetify 主题
│   ├── LightTheme.ts
│   └── DarkTheme.ts
├── types/               # TypeScript 类型声明
├── utils/               # 工具函数
│   ├── routerReadiness.mjs
│   ├── confirmDialog.ts
│   ├── toast.js
│   └── ...
└── views/               # 页面组件
    ├── authentication/  # 认证页面
    ├── alkaid/          # Alkaid 功能模块
    ├── extension/       # 插件管理页面
    ├── knowledge-base/  # 知识库页面
    ├── persona/         # Persona 管理页面
    ├── stats/           # 统计页面
    ├── AboutPage.vue
    ├── ChatPage.vue
    ├── ConfigPage.vue
    ├── ConsolePage.vue
    ├── CronJobPage.vue
    ├── ExtensionPage.vue
    ├── PlatformPage.vue
    ├── ProviderPage.vue
    ├── SessionManagementPage.vue
    ├── Settings.vue
    ├── SubAgentPage.vue
    ├── TracePage.vue
    └── WelcomePage.vue
```

## 3. 核心架构设计

### 3.1 路由系统

采用 **Hash 模式**（`createWebHashHistory`），由三组路由构成：

```
┌─────────────────────────────────────────────────────────────┐
│                      Router                                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  MainRoutes     │  │ AuthRoutes   │  │ ChatBoxRoutes │ │
│  │  /main/*        │  │ /auth/*      │  │ /chatbox/*    │ │
│  │  (需认证)        │  │ (公开)        │  │ (需认证)       │ │
│  └─────────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**路由守卫逻辑** (`router/index.ts`):
- 公开页面：`/auth/login`
- 需要认证的路由通过 `meta.requiresAuth: true` 标记
- 未登录用户访问受保护路由时，重定向到 `/auth/login`
- 已登录用户访问登录页时，重定向到 `/welcome`
- 路由切换时显示加载进度条

### 3.2 状态管理 (Pinia)

| Store | 用途 |
|-------|------|
| `auth` | 用户登录/登出、JWT token 管理、onboarding 状态检查 |
| `customizer` | UI 主题（亮/暗）、侧边栏状态、字体主题 |
| `toast` | 全局 Toast 通知队列 |
| `common` | 通用状态（如 AstrBot 版本信息） |
| `personaStore` | Persona 相关状态 |
| `routerLoading` | 路由切换加载进度 |

### 3.3 布局系统

**FullLayout.vue** — 主应用布局：
```
┌────────────────────────────────────────┐
│           VerticalHeader              │  ← 顶部导航栏
├─────────────┬──────────────────────────┤
│             │                          │
│  Vertical   │      <RouterView>        │  ← 主内容区
│  Sidebar    │                          │
│             │                          │
└─────────────┴──────────────────────────┘
```

**特殊处理**：当路由为 `/chat` 或 `/chat/*` 时，侧边栏隐藏，Chat 组件全局挂载在布局中。

### 3.4 国际化 (i18n)

自实现的轻量级 i18n 系统（未使用 vue-i18n）：

- **支持语言**：`zh-CN`（默认）、`en-US`、`ru-RU`
- **翻译数据源**：静态导入 `translations.ts`
- **动态合并**：支持插件通过 `mergeDynamicTranslations()` 注入翻译
- **语言切换**：通过 `window.dispatchEvent('astrbot-locale-changed')` 通知全应用

## 4. API 通信机制

### Axios 拦截器 (`main.ts`)

```typescript
// 请求拦截器：自动附加 JWT token 和 Accept-Language
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  const locale = localStorage.getItem('astrbot-locale');
  if (locale) {
    config.headers['Accept-Language'] = locale;
  }
  return config;
});
```

同时对原生 `fetch` 做了相同处理，确保部分使用 fetch 的代码也能正确携带认证头。

### API 代理

开发环境下，Vite 代理 `/api` 请求到 `http://127.0.0.1:6185/`，避免跨域问题。

## 5. 主题系统

### Vuetify 主题配置

```typescript
// vite.config.ts 中配置
server: {
  proxy: {
    '/api': { target: 'http://127.0.0.1:6185/', changeOrigin: true, ws: true }
  }
}
```

### 亮色/暗色主题

- `PurpleTheme` — 紫色主题（亮色）
- `PurpleThemeDark` — 紫色主题（暗色）

主题保存在 `localStorage` 中（`uiTheme` 键），可在运行时动态切换。

## 6. 关键组件关系

```
App.vue
├── RouterView
│   ├── BlankLayout (认证页)
│   │   └── LoginPage.vue
│   └── FullLayout (主应用)
│       ├── VerticalHeader.vue
│       ├── VerticalSidebar.vue
│       └── RouterView
│           ├── WelcomePage.vue
│           ├── ExtensionPage.vue
│           ├── ChatPage.vue
│           ├── ConfigPage.vue
│           ├── KnowledgeBase (知识库)
│           ├── Persona (Persona 管理)
│           └── ...
```

## 7. 重要工具和特性

| 功能 | 实现 |
|------|------|
| Monaco Editor | `@guolao/vue-monaco-editor` + 自定义 worker 配置 |
| Markdown 渲染 | `markdown-it` + `stream-markdown` |
| 语法高亮 | `shiki` (Text-to-Image 场景使用受限包) |
| 图表 | `vue3-apexcharts` (ApexCharts) |
| 富文本编辑 | `@tiptap/vue-3` (基于 ProseMirror) |
| 二维码 | `qrcode` |
| 数学公式 | `katex` |
| Mermaid 图表 | `mermaid` |
| 打印支持 | `vue3-print-nb` |

## 8. 构建配置

- **开发服务器**：`vite --host`（监听 0.0.0.0:3000）
- **构建命令**：`vue-tsc --noEmit && vite build`
- **MDI 图标子集化**：构建时运行 `scripts/subset-mdi-font.mjs`，只打包使用的图标
- **T2I Shiki 运行时**：Vite 插件在构建时嵌入 `t2i/shiki_runtime.iife.js`

## 9. 总结

AstrBot Dashboard 是一个功能完善的管理前端，采用典型的 Vue 3 企业级应用架构：

1. **模块化清晰**：页面、组件、状态、路由、国际化均按职责分离
2. **Composition API 为主**：大量使用 `composables` 实现逻辑复用
3. **Vuetify 生态**：基于 Vuetify 3 构建完整 UI，主题系统支持亮暗切换
4. **认证安全**：JWT token 通过 Axios/fetch 拦截器自动附加
5. **国际化完善**：内置三种语言支持，支持插件动态注入翻译
6. **构建优化**：MDI 图标子集化、T2I Shiki 运行时嵌入等定制优化
