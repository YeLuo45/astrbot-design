import { defineConfig } from "vitepress";

export default defineConfig({
  title: "AstrBot Design",
  description: "AstrBot 架构分析与扩展设计文档",

  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
  ],

  themeConfig: {
    logo: "/astrbot_banner.png",

    nav: [
      { text: "Home", link: "/" },
      { text: "Architecture", link: "/architecture" },
      { text: "API", link: "/api" },
      { text: "Dashboard", link: "/dashboard" },
      { text: 'MCP', link: '/mcp' },
      { text: 'Agent Runner', link: '/agent-runner' },
      { text: 'Platform Adapter', link: '/platform-adapter' },
      { text: 'Extensions', link: '/extension-directions' },
      { text: 'Plugin Guide', link: '/plugin-development' }
    ],

    sidebar: [
      {
        text: "Documentation",
        items: [
          { text: "Home", link: "/" },
          { text: "架构分析", link: "/architecture" },
          { text: "API 接口分析", link: "/api" },
          { text: "Dashboard 架构", link: "/dashboard" },
          { text: "MCP 集成", link: "/mcp" },
          { text: "Agent 执行器", link: "/agent-runner" },
          { text: "平台适配器", link: "/platform-adapter" },
          { text: "扩展方向", link: "/extension-directions" },
          { text: "插件开发指南", link: "/plugin-development" },
        ],
      },
    ],

    socialLinks: [
      { icon: "github", link: "https://github.com/Sonic-Yoda/AstrBot" }
    ],

    footer: {
      message: "基于 AstrBot 开源项目构建",
      copyright: "Copyright © 2024-present AstrBot Contributors"
    },
  },

  base: "/astrbot-design/",

  rewrites: {},
});
