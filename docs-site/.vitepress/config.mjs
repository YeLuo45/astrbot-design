import { defineConfig } from "vitepress";

export default defineConfig({
  title: "AstrBot Design",
  description: "AstrBot 架构分析与扩展设计文档",
  
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Architecture", link: "/architecture" },
      { text: "API", link: "/api" },
      { text: "Dashboard", link: "/dashboard" },
            { text: 'MCP', link: '/mcp' },
            { text: 'Agent Runner', link: '/agent-runner' },
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
          { text: "扩展方向", link: "/extension-directions" },
          { text: "插件开发指南", link: "/plugin-development" },
        ],
      },
    ],
  },

  rewrites: {},
});
