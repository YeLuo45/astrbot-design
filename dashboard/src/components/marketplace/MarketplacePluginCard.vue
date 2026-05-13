<script setup lang="ts">
/**
 * MarketplacePluginCard.vue - Card component for plugin display
 */
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { PluginEntry } from './types';

const { t } = useI18n();

const props = defineProps<{
  plugin: PluginEntry;
}>();

const emit = defineEmits<{
  install: [plugin: PluginEntry];
  open: [plugin: PluginEntry];
}>();

const categoryColor = computed(() => {
  const colors: Record<string, string> = {
    ai: 'purple',
    tools: 'blue',
    integration: 'green',
    automation: 'orange',
    other: 'grey',
  };
  return colors[props.plugin.category] || 'grey';
});

const formatDownloads = (count: number) => {
  if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M';
  if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
  return count.toString();
};

const handleInstall = (e: Event) => {
  e.stopPropagation();
  emit('install', props.plugin);
};

const handleOpen = () => {
  emit('open', props.plugin);
};
</script>

<template>
  <v-card
    class="rounded-lg d-flex flex-column plugin-card"
    variant="outlined"
    elevation="0"
    :ripple="false"
    @click="handleOpen"
  >
    <v-card-text class="plugin-card-content">
      <!-- Plugin Icon -->
      <div class="plugin-cover">
        <v-icon size="48" color="primary">mdi-plugin</v-icon>
      </div>

      <!-- Plugin Info -->
      <div class="plugin-info">
        <div class="d-flex align-center mb-2">
          <div class="font-weight-bold plugin-title text-truncate">
            {{ plugin.name }}
          </div>
          <v-chip
            :color="categoryColor"
            size="x-small"
            label
            class="ml-2"
          >
            {{ plugin.category }}
          </v-chip>
        </div>

        <div class="text-caption text-grey mb-2">
          {{ t('marketplace.by') }} {{ plugin.author_name }}
        </div>

        <p class="text-body-2 text-truncate-2 mb-3">
          {{ plugin.description }}
        </p>

        <!-- Tags -->
        <div class="mb-3">
          <v-chip
            v-for="tag in plugin.tags.slice(0, 3)"
            :key="tag"
            size="x-small"
            variant="outlined"
            class="mr-1"
          >
            {{ tag }}
          </v-chip>
        </div>

        <!-- Stats -->
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon size="14" color="amber" class="mr-1">mdi-star</v-icon>
            <span class="text-caption">{{ plugin.rating_average.toFixed(1) }}</span>
            <span class="text-caption text-grey ml-2">
              {{ formatDownloads(plugin.download_count) }}
              <v-icon size="12" class="ml-1">mdi-download</v-icon>
            </span>
          </div>
          
          <v-btn
            color="primary"
            size="x-small"
            variant="tonal"
            @click="handleInstall"
          >
            {{ t('marketplace.install') }}
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.plugin-card {
  height: 100%;
  cursor: pointer;
  transition: border-color 0.2s;
}

.plugin-card:hover {
  border-color: rgb(var(--v-theme-primary));
}

.plugin-card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.plugin-cover {
  width: 100%;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.1), rgba(var(--v-theme-primary), 0.05));
  border-radius: 8px;
  margin-bottom: 12px;
}

.plugin-info {
  flex: 1;
}

.plugin-title {
  font-size: 1rem;
  max-width: 150px;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 2.8em;
}
</style>
