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
│   ├── folder/         # 文件夹树通用组件
│   ├── platform/       # 平台相关组件
│   ├── provider/       # 提供者相关组件
│   └── shared/         # 共享全局组件
├── composables/         # Vue Composition API 组合函数
│   ├── useConversations.ts
│   ├── useMessages.ts
│   ├── useSessions.ts
│   └── ...
├── i18n/                # 国际化系统（zh-CN, en-US, ru-RU）
├── layouts/             # 页面布局（blank/full）
├── plugins/             # Vuetify 插件配置
├── router/              # 路由配置（Hash 模式）
├── stores/              # Pinia 状态管理
│   ├── auth.ts          # JWT 认证
│   ├── customizer.ts    # UI 主题
│   ├── personaStore.ts  # Persona 状态
│   └── toast.js         # Toast 通知
├── views/               # 页面组件
│   ├── ChatPage.vue
│   ├── ConfigPage.vue
│   ├── ExtensionPage.vue
│   ├── PlatformPage.vue
│   ├── ProviderPage.vue
│   └── ...
└── theme/               # Vuetify 主题（亮/暗）
```

## 3. 核心架构设计

### 3.1 路由系统

采用 **Hash 模式**（`createWebHashHistory`），由三组路由构成：

```
Router
├── MainRoutes     /main/*   (需认证)
├── AuthRoutes     /auth/*   (公开)
└── ChatBoxRoutes  /chatbox/* (需认证)
```

**路由守卫逻辑**:
- 公开页面：`/auth/login`
- 受保护路由通过 `meta.requiresAuth: true` 标记
- 未登录 → 重定向到 `/auth/login`
- 已登录访问登录页 → 重定向到 `/welcome`

### 3.2 状态管理 (Pinia)

| Store | 用途 |
|-------|------|
| `auth` | 用户登录/登出、JWT token 管理 |
| `customizer` | UI 主题（亮/暗）、侧边栏状态 |
| `toast` | 全局 Toast 通知队列 |
| `common` | 通用状态（如 AstrBot 版本） |
| `personaStore` | Persona 相关状态 |

### 3.3 布局系统

```
┌────────────────────────────────────────┐
│           VerticalHeader               │  ← 顶部导航栏
├─────────────┬──────────────────────────┤
│             │                          │
│  Vertical   │      <RouterView>        │  ← 主内容区
│  Sidebar    │                          │
│             │                          │
└─────────────┴──────────────────────────┘
```

特殊处理：路由为 `/chat` 或 `/chat/*` 时，侧边栏隐藏，Chat 组件全局挂载。

### 3.4 国际化 (i18n)

自实现的轻量级 i18n 系统（未使用 vue-i18n）：

- **支持语言**：`zh-CN`（默认）、`en-US`、`ru-RU`
- **翻译数据源**：静态导入 `translations.ts`
- **动态合并**：支持插件通过 `mergeDynamicTranslations()` 注入翻译
- **语言切换**：通过 `window.dispatchEvent('astrbot-locale-changed')` 通知全应用

## 4. API 通信机制

### Axios 拦截器

```typescript
// 请求拦截器：自动附加 JWT token 和 Accept-Language
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});
```

### API 代理

开发环境下，Vite 代理 `/api` 请求到 `http://127.0.0.1:6185/`：

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': { target: 'http://127.0.0.1:6185/', changeOrigin: true, ws: true }
  }
}
```

## 5. 主题系统

- **亮色主题**：`PurpleTheme`
- **暗色主题**：`PurpleThemeDark`

主题保存在 `localStorage`（`uiTheme` 键），支持运行时动态切换。

## 6. 组件关系

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
│           ├── ChatPage.vue
│           ├── ExtensionPage.vue
│           ├── ProviderPage.vue
│           └── ...
```

## 7. 关键工具库

| 功能 | 实现 |
|------|------|
| Monaco Editor | `@guolao/vue-monaco-editor` |
| Markdown 渲染 | `markdown-it` + `stream-markdown` |
| 图表 | `vue3-apexcharts` |
| 富文本编辑 | `@tiptap/vue-3` |
| 数学公式 | `katex` |
| Mermaid 图表 | `mermaid` |
| 二维码 | `qrcode` |

## 8. 构建配置

- **开发服务器**：`vite --host`（监听 0.0.0.0:3000）
- **构建命令**：`vue-tsc --noEmit && vite build`
- **MDI 图标子集化**：构建时只打包使用的图标
- **Shiki 运行时**：Vite 插件在构建时嵌入 T2I 相关运行时

## 9. 总结

AstrBot Dashboard 采用典型的 Vue 3 企业级应用架构：

1. **模块化清晰**：页面、组件、状态、路由、国际化按职责分离
2. **Composition API 为主**：大量 `composables` 实现逻辑复用
3. **Vuetify 生态**：完整 UI + 亮暗主题切换
4. **认证安全**：JWT token 通过 Axios/fetch 拦截器自动附加
5. **国际化完善**：内置三种语言，支持插件动态注入翻译
6. **构建优化**：MDI 图标子集化等定制优化
