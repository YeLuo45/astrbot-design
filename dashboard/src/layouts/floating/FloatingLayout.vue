<script setup lang="ts">
import { RouterView, useRoute, useRouter } from "vue-router";
import { ref, computed, onMounted, onUnmounted } from "vue";
import VerticalSidebarVue from "@/layouts/full/vertical-sidebar/VerticalSidebar.vue";
import VerticalHeaderVue from "@/layouts/full/vertical-header/VerticalHeader.vue";
import MigrationDialog from "@/components/shared/MigrationDialog.vue";
import ReadmeDialog from "@/components/shared/ReadmeDialog.vue";
import Chat from "@/components/chat/Chat.vue";
import { useCustomizerStore } from "@/stores/customizer";
import { useRouterLoadingStore } from "@/stores/routerLoading";
import { useCommonStore } from "@/stores/common";
import { useI18n } from "@/i18n/composables";

const FIRST_NOTICE_SEEN_KEY = "astrbot:first_notice_seen:v1";

const customizer = useCustomizerStore();
const commonStore = useCommonStore();
const { locale } = useI18n();
const route = useRoute();
const router = useRouter();
const routerLoadingStore = useRouterLoadingStore();

// Navigation items for keyboard shortcuts
const navItems = [
  { path: "/welcome", icon: "mdi-hand-wave-outline", label: "Welcome", key: "1" },
  { path: "/chat", icon: "mdi-chat", label: "Chat", key: "2", isAction: true },
  { path: "/platforms", icon: "mdi-robot", label: "Platforms", key: "3" },
  { path: "/providers", icon: "mdi-creation", label: "Providers", key: "4" },
  { path: "/extension", icon: "mdi-puzzle", label: "Extensions", key: "5" },
  { path: "/knowledge-base", icon: "mdi-book-open-variant", label: "Knowledge Base", key: "6" },
  { path: "/persona", icon: "mdi-heart", label: "Persona", key: "7" },
  { path: "/settings", icon: "mdi-cog", label: "Settings", key: "8" },
];

const currentNavIndex = computed(() => {
  const path = route.path;
  if (path.startsWith("/chat")) return 1;
  const idx = navItems.findIndex(item => !item.isAction && path.startsWith(item.path));
  return idx >= 0 ? idx : 0;
});

// Floating mode: always show sidebar as icons only
const floatingSidebar = ref(true);
const showSidebar = ref(true);

// Chat panel floating state
const chatFloating = ref(false);
const chatPanelWidth = ref(420);
const chatPanelHeight = ref(600);
const chatPanelRight = ref(24);
const chatPanelBottom = ref(80);
const isChatDragging = ref(false);
const isChatResizing = ref(false);
const chatPanelTheme = ref<'dark' | 'light'>('dark');

// Keyboard navigation state
const focusedNavIndex = ref(-1);

const migrationDialog = ref<InstanceType<typeof MigrationDialog> | null>(null);
const showFirstNoticeDialog = ref(false);

const checkMigration = async (): Promise<boolean> => {
  try {
    const response = await fetch("/api/stat/version");
    const data = await response.json();
    if (data.status === "ok") {
      commonStore.setAstrBotVersion(
        data.data?.version,
        data.data?.dashboard_version,
      );
    }
    if (data.status === "ok" && data.data.need_migration) {
      if (migrationDialog.value && typeof migrationDialog.value.open === "function") {
        const result = await migrationDialog.value.open();
        if (result.success) {
          window.location.reload();
        }
      }
      return true;
    }
  } catch (error) {
    console.error("Failed to check migration status:", error);
  }
  return false;
};

const maybeShowFirstNotice = async () => {
  if (localStorage.getItem(FIRST_NOTICE_SEEN_KEY) === "1") return;
  try {
    const response = await fetch(`/api/stat/first-notice?locale=${locale.value}`);
    const data = await response.json();
    if (data.status === "ok" && typeof data.data?.content === "string" && data.data.content.trim().length > 0) {
      showFirstNoticeDialog.value = true;
    } else {
      localStorage.setItem(FIRST_NOTICE_SEEN_KEY, "1");
    }
  } catch (error) {
    console.error("Failed to load first notice:", error);
  }
};

const onFirstNoticeDialogUpdate = (visible: boolean) => {
  showFirstNoticeDialog.value = visible;
  if (!visible) localStorage.setItem(FIRST_NOTICE_SEEN_KEY, "1");
};

// Keyboard navigation: J/K to navigate, ESC to close chat
function handleKeydown(e: KeyboardEvent) {
  // Skip if user is typing in an input
  const target = e.target as HTMLElement;
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
    return;
  }

  // ESC - Close floating chat panel
  if (e.key === "Escape") {
    if (chatFloating.value) {
      chatFloating.value = false;
      e.preventDefault();
      return;
    }
    // Clear nav focus
    if (focusedNavIndex.value >= 0) {
      focusedNavIndex.value = -1;
      e.preventDefault();
    }
    return;
  }

  // J - Navigate down (next item)
  if (e.key === "j" || e.key === "J") {
    if (focusedNavIndex.value < 0) {
      focusedNavIndex.value = 0;
    } else {
      focusedNavIndex.value = (focusedNavIndex.value + 1) % navItems.length;
    }
    e.preventDefault();
    return;
  }

  // K - Navigate up (previous item)
  if (e.key === "k" || e.key === "K") {
    if (focusedNavIndex.value < 0) {
      focusedNavIndex.value = navItems.length - 1;
    } else {
      focusedNavIndex.value = focusedNavIndex.value - 1 < 0 ? navItems.length - 1 : focusedNavIndex.value - 1;
    }
    e.preventDefault();
    return;
  }

  // Enter - Activate focused nav item
  if (e.key === "Enter" && focusedNavIndex.value >= 0) {
    const item = navItems[focusedNavIndex.value];
    if (item.isAction) {
      chatFloating.value = !chatFloating.value;
    } else {
      router.push(item.path);
    }
    focusedNavIndex.value = -1;
    e.preventDefault();
    return;
  }

  // Number keys 1-8 for direct navigation
  const num = parseInt(e.key);
  if (num >= 1 && num <= 8) {
    const item = navItems[num - 1];
    if (item.isAction) {
      chatFloating.value = !chatFloating.value;
    } else {
      router.push(item.path);
    }
    e.preventDefault();
  }
}

onMounted(() => {
  setTimeout(async () => {
    const migrationPending = await checkMigration();
    if (!migrationPending) await maybeShowFirstNotice();
  }, 1000);
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});

// Toggle floating chat panel
function toggleChatFloating() {
  chatFloating.value = !chatFloating.value;
}

// Chat panel drag
let chatDragOffsetX = 0;
let chatDragOffsetY = 0;

function startChatDrag(e: MouseEvent) {
  isChatDragging.value = true;
  const rect = (e.target as HTMLElement).closest('.floating-chat-panel')?.getBoundingClientRect();
  if (rect) {
    chatDragOffsetX = e.clientX - rect.left;
    chatDragOffsetY = e.clientY - rect.top;
  }
  document.addEventListener('mousemove', onChatMouseMove);
  document.addEventListener('mouseup', onChatMouseUp);
}

function onChatMouseMove(e: MouseEvent) {
  if (!isChatDragging.value) return;
  chatPanelRight.value = window.innerWidth - e.clientX - chatDragOffsetX;
  chatPanelBottom.value = window.innerHeight - e.clientY - chatDragOffsetY;
}

function onChatMouseUp() {
  isChatDragging.value = false;
  document.removeEventListener('mousemove', onChatMouseMove);
  document.removeEventListener('mouseup', onChatMouseUp);
}

// Chat panel resize
function startChatResize(e: MouseEvent) {
  isChatResizing.value = true;
  e.preventDefault();
  document.addEventListener('mousemove', onChatResizeMove);
  document.addEventListener('mouseup', onChatResizeEnd);
}

function onChatResizeMove(e: MouseEvent) {
  if (!isChatResizing.value) return;
  chatPanelWidth.value = Math.max(320, Math.min(800, e.clientX - (window.innerWidth - chatPanelRight.value - chatPanelWidth.value)));
  chatPanelHeight.value = Math.max(400, Math.min(900, e.clientY - (window.innerHeight - chatPanelBottom.value - chatPanelHeight.value)));
}

function onChatResizeEnd() {
  isChatResizing.value = false;
  document.removeEventListener('mousemove', onChatResizeMove);
  document.removeEventListener('mouseup', onChatResizeEnd);
}

// Navigate to item
function navigateTo(path: string) {
  router.push(path);
}

// Toggle chat panel theme
function toggleChatTheme() {
  chatPanelTheme.value = chatPanelTheme.value === 'dark' ? 'light' : 'dark';
}
</script>

<template>
  <v-locale-provider>
    <v-app
      :theme="useCustomizerStore().uiTheme"
      :class="[customizer.fontTheme, 'floating-layout']"
    >
      <!-- Keyboard shortcuts hint -->
      <div class="keyboard-hint" v-if="focusedNavIndex >= 0">
        <v-chip size="small" color="primary" class="mr-1">J↓</v-chip>
        <v-chip size="small" color="primary" class="mr-1">K↑</v-chip>
        <v-chip size="small" color="primary" class="mr-1">Enter</v-chip>
        <span class="text-caption">{{ navItems[focusedNavIndex]?.label }}</span>
      </div>

      <!-- Top Header Bar -->
      <VerticalHeaderVue />

      <!-- Floating Icon Sidebar (left edge) -->
      <v-navigation-drawer
        v-model="showSidebar"
        permanent
        left
        rail
        rail-width="56"
        class="floating-sidebar"
        elevation="2"
      >
        <div class="floating-sidebar-icons">
          <div
            v-for="(item, idx) in navItems"
            :key="item.path"
            class="nav-item-wrapper"
            :class="{ focused: focusedNavIndex === idx }"
            :title="`${item.label} [${item.key}]`"
          >
            <v-btn
              icon
              variant="text"
              size="small"
              :color="(item.isAction ? chatFloating : route.path.startsWith(item.path)) && focusedNavIndex !== idx ? 'primary' : focusedNavIndex === idx ? 'secondary' : undefined"
              :to="item.isAction ? undefined : item.path"
              @click="item.isAction ? toggleChatFloating() : navigateTo(item.path)"
              class="nav-btn"
            >
              <v-icon size="22">{{ item.icon }}</v-icon>
            </v-btn>
            <span class="nav-key-hint">{{ item.key }}</span>
          </div>

          <v-divider class="my-2" />
        </div>
      </v-navigation-drawer>

      <!-- Main Content Area -->
      <v-main
        :style="{
          height: 'calc(100vh - 56px)',
          overflow: 'auto',
          marginLeft: '56px',
        }"
      >
        <v-container fluid class="page-wrapper pa-4">
          <RouterView />
        </v-container>
      </v-main>

      <!-- Floating Chat Panel -->
      <div
        v-if="chatFloating"
        class="floating-chat-panel"
        :class="chatPanelTheme === 'dark' ? 'theme-dark' : 'theme-light'"
        :style="{
          position: 'fixed',
          right: chatPanelRight + 'px',
          bottom: chatPanelBottom + 'px',
          width: chatPanelWidth + 'px',
          height: chatPanelHeight + 'px',
          zIndex: 2000,
        }"
      >
        <!-- Drag Handle -->
        <div
          class="chat-panel-header"
          :class="chatPanelTheme === 'dark' ? 'theme-dark' : 'theme-light'"
          style="cursor: move;"
          @mousedown.left="startChatDrag"
        >
          <v-icon size="18" class="mr-2">mdi-chat</v-icon>
          <span class="text-body-2">Chat</span>
          <v-spacer />
          <v-btn icon size="x-small" variant="text" @click="toggleChatTheme">
            <v-icon size="18">{{ chatPanelTheme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
          </v-btn>
          <v-btn icon size="x-small" variant="text" @click="chatFloating = false">
            <v-icon size="18">mdi-close</v-icon>
          </v-btn>
        </div>

        <!-- Resize Handle -->
        <div
          class="chat-panel-resize-handle"
          @mousedown.left="startChatResize"
        />

        <!-- Chat Component -->
        <div style="height: calc(100% - 40px); overflow: hidden;">
          <Chat :active="true" />
        </div>
      </div>

      <MigrationDialog ref="migrationDialog" />
      <ReadmeDialog
        :show="showFirstNoticeDialog"
        mode="first-notice"
        @update:show="onFirstNoticeDialogUpdate"
      />
    </v-app>
  </v-locale-provider>
</template>

<style scoped>
.floating-layout {
  background: rgb(var(--v-theme-background));
}

.floating-sidebar {
  margin-top: 56px !important;
  height: calc(100vh - 56px) !important;
  background: rgb(var(--v-theme-surface)) !important;
}

.floating-sidebar-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  gap: 4px;
}

.nav-item-wrapper {
  position: relative;
  border-radius: 8px;
  transition: all 0.15s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nav-item-wrapper.focused {
  background: rgba(var(--v-theme-primary), 0.15);
  transform: scale(1.1);
}

.nav-key-hint {
  font-size: 9px;
  color: rgba(128, 128, 128, 0.7);
  margin-top: 2px;
  line-height: 1;
}

.nav-btn {
  transition: all 0.15s ease;
}

.keyboard-hint {
  position: fixed;
  bottom: 16px;
  left: 72px;
  z-index: 9999;
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  color: white;
}

.floating-chat-panel {
  background: rgb(var(--v-theme-surface));
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.floating-chat-panel.theme-dark {
  background: #1e1e2e;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.floating-chat-panel.theme-light {
  background: #fafafa;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.chat-panel-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  height: 40px;
  flex-shrink: 0;
}

.chat-panel-header.theme-dark {
  background: #2d2d3d;
  color: #e0e0e0;
}

.chat-panel-header.theme-light {
  background: #ffffff;
  color: #333333;
  border-bottom: 1px solid #e0e0e0;
}

.chat-panel-resize-handle {
  position: absolute;
  top: 0;
  left: 0;
  width: 8px;
  height: 8px;
  cursor: nwse-resize;
}
</style>
