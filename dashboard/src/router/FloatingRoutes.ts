import {
  EXTENSION_DETAILS_ROUTE_NAME,
  EXTENSION_ROUTE_NAME
} from './routeConstants.mjs';

const FloatingRoutes = {
  path: '/floating',
  meta: {
    requiresAuth: true
  },
  redirect: '/floating/welcome',
  component: () => import('@/layouts/floating/FloatingLayout.vue'),
  children: [
    {
      name: 'FloatingWelcome',
      path: '/floating/welcome',
      component: () => import('@/views/WelcomePage.vue')
    },
    {
      name: 'FloatingExtension',
      path: '/floating/extension',
      component: () => import('@/views/ExtensionPage.vue')
    },
    {
      name: 'FloatingPluginPage',
      path: '/floating/plugin-page/:pluginName/:pageName',
      component: () => import('@/views/PluginPagePage.vue')
    },
    {
      name: 'FloatingExtensionDetails',
      path: '/floating/extension/:pluginId',
      component: () => import('@/views/ExtensionPage.vue')
    },
    {
      name: 'FloatingExtensionMarketplace',
      path: '/floating/extension-marketplace',
      component: () => import('@/views/ExtensionPage.vue')
    },
    {
      name: 'FloatingPlatforms',
      path: '/floating/platforms',
      component: () => import('@/views/PlatformPage.vue')
    },
    {
      name: 'FloatingProviders',
      path: '/floating/providers',
      component: () => import('@/views/ProviderPage.vue')
    },
    {
      name: 'FloatingConfigs',
      path: '/floating/config',
      component: () => import('@/views/ConfigPage.vue')
    },
    {
      path: '/floating/normal',
      redirect: '/floating/config#normal'
    },
    {
      path: '/floating/system',
      redirect: '/floating/config#system'
    },
    {
      name: 'FloatingStats',
      path: '/floating/dashboard',
      component: () => import('@/views/stats/StatsPage.vue')
    },
    {
      name: 'FloatingConversation',
      path: '/floating/conversation',
      component: () => import('@/views/ConversationPage.vue')
    },
    {
      name: 'FloatingSessionManagement',
      path: '/floating/session-management',
      component: () => import('@/views/SessionManagementPage.vue')
    },
    {
      name: 'FloatingPersona',
      path: '/floating/persona',
      component: () => import('@/views/PersonaPage.vue')
    },
    {
      name: 'FloatingSubAgent',
      path: '/floating/subagent',
      component: () => import('@/views/SubAgentPage.vue')
    },
    {
      name: 'FloatingCronJobs',
      path: '/floating/cron',
      component: () => import('@/views/CronJobPage.vue')
    },
    {
      name: 'FloatingConsole',
      path: '/floating/console',
      component: () => import('@/views/ConsolePage.vue')
    },
    {
      name: 'FloatingTrace',
      path: '/floating/trace',
      component: () => import('@/views/TracePage.vue')
    },
    {
      name: 'FloatingNativeKnowledgeBase',
      path: '/floating/knowledge-base',
      component: () => import('@/views/knowledge-base/index.vue'),
      children: [
        {
          path: '',
          name: 'FloatingKBList',
          component: () => import('@/views/knowledge-base/KBList.vue')
        },
        {
          path: ':kbId',
          name: 'FloatingKBDetail',
          component: () => import('@/views/knowledge-base/KBDetail.vue'),
          props: true
        },
        {
          path: ':kbId/document/:docId',
          name: 'FloatingDocumentDetail',
          component: () => import('@/views/knowledge-base/DocumentDetail.vue'),
          props: true
        }
      ]
    },
    {
      name: 'FloatingKnowledgeBase',
      path: '/floating/alkaid/knowledge-base',
      component: () => import('@/views/alkaid/KnowledgeBase.vue'),
    },
    {
      name: 'FloatingSettings',
      path: '/floating/settings',
      component: () => import('@/views/Settings.vue')
    },
    {
      name: 'FloatingAbout',
      path: '/floating/about',
      component: () => import('@/views/AboutPage.vue')
    }
  ]
};

export default FloatingRoutes;
