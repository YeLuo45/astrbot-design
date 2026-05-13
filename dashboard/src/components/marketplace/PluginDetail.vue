<script setup lang="ts">
/**
 * PluginDetail.vue - Detail page with install button
 */
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { marketplaceClient } from './marketplace';
import type { PluginEntry } from './types';

const { t } = useI18n();
const route = useRoute();

const plugin = ref<PluginEntry | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const installing = ref(false);
const installMessage = ref('');

const slug = computed(() => route.params.slug as string);

const fetchPlugin = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await marketplaceClient.getPlugin(slug.value);
    if (result) {
      plugin.value = result;
    } else {
      error.value = t('marketplace.plugin_not_found');
    }
  } catch (e) {
    error.value = t('marketplace.error_loading_plugin');
    console.error('Failed to fetch plugin:', e);
  } finally {
    loading.value = false;
  }
};

const handleInstall = async () => {
  if (!plugin.value) return;
  
  installing.value = true;
  installMessage.value = '';
  
  try {
    const result = await marketplaceClient.installPlugin(plugin.value);
    installMessage.value = result.message;
    if (!result.success) {
      // Show error via alert
    }
  } catch (e) {
    installMessage.value = t('marketplace.install_failed');
  } finally {
    installing.value = false;
  }
};

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString();
};

const formatDownloads = (count: number) => {
  if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M';
  if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
  return count.toString();
};

onMounted(() => {
  fetchPlugin();
});
</script>

<template>
  <div class="plugin-detail">
    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-center align-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-8">
      <v-alert type="error" variant="tonal">{{ error }}</v-alert>
      <v-btn class="mt-4" to="/marketplace">{{ t('marketplace.back_to_marketplace') }}</v-btn>
    </div>

    <!-- Plugin Details -->
    <v-card v-else-if="plugin" variant="outlined">
      <v-row no-gutters>
        <!-- Plugin Icon -->
        <v-col cols="12" md="3" class="pa-4 text-center">
          <div class="plugin-icon-wrapper">
            <v-icon size="96" color="primary">mdi-plugin</v-icon>
          </div>
        </v-col>

        <!-- Plugin Info -->
        <v-col cols="12" md="9">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <h1 class="text-h4 mb-2">{{ plugin.name }}</h1>
                <div class="text-body-2 text-grey mb-4">
                  {{ t('marketplace.by') }} {{ plugin.author_name }}
                </div>
              </div>
              
              <!-- Install Button -->
              <v-btn
                color="primary"
                size="large"
                :loading="installing"
                @click="handleInstall"
              >
                <v-icon start>mdi-download</v-icon>
                {{ t('marketplace.install') }}
              </v-btn>
            </div>

            <!-- Install Message -->
            <v-alert
              v-if="installMessage"
              :type="installMessage.includes('success') ? 'success' : 'error'"
              variant="tonal"
              class="mb-4"
            >
              {{ installMessage }}
            </v-alert>

            <!-- Stats -->
            <v-row class="mb-4">
              <v-col cols="4">
                <div class="text-center">
                  <div class="text-h6">{{ formatDownloads(plugin.download_count) }}</div>
                  <div class="text-caption text-grey">{{ t('marketplace.downloads') }}</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="text-center">
                  <div class="text-h6">
                    <v-icon size="20" color="amber">mdi-star</v-icon>
                    {{ plugin.rating_average.toFixed(1) }}
                  </div>
                  <div class="text-caption text-grey">{{ t('marketplace.rating') }} ({{ plugin.rating_count }})</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="text-center">
                  <div class="text-h6">v{{ plugin.version }}</div>
                  <div class="text-caption text-grey">{{ t('marketplace.version') }}</div>
                </div>
              </v-col>
            </v-row>

            <!-- Description -->
            <div class="mb-4">
              <h3 class="text-h6 mb-2">{{ t('marketplace.description') }}</h3>
              <p>{{ plugin.description }}</p>
            </div>

            <!-- Tags -->
            <div class="mb-4">
              <v-chip
                v-for="tag in plugin.tags"
                :key="tag"
                size="small"
                class="mr-2"
              >
                {{ tag }}
              </v-chip>
            </div>

            <!-- Meta Info -->
            <v-divider class="my-4" />
            
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title class="d-flex justify-space-between">
                  <span class="text-grey">{{ t('marketplace.category') }}</span>
                  <span>{{ plugin.category }}</span>
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title class="d-flex justify-space-between">
                  <span class="text-grey">{{ t('marketplace.min_version') }}</span>
                  <span>{{ plugin.min_astrbot_version }}</span>
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item v-if="plugin.license">
                <v-list-item-title class="d-flex justify-space-between">
                  <span class="text-grey">{{ t('marketplace.license') }}</span>
                  <span>{{ plugin.license }}</span>
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title class="d-flex justify-space-between">
                  <span class="text-grey">{{ t('marketplace.updated') }}</span>
                  <span>{{ formatDate(plugin.updated_at) }}</span>
                </v-list-item-title>
              </v-list-item>
            </v-list>

            <!-- Links -->
            <div class="mt-4">
              <v-btn
                v-if="plugin.repository"
                :href="plugin.repository"
                target="_blank"
                variant="text"
                size="small"
              >
                <v-icon start>mdi-github</v-icon>
                {{ t('marketplace.repository') }}
              </v-btn>
              
              <v-btn
                v-if="plugin.homepage"
                :href="plugin.homepage"
                target="_blank"
                variant="text"
                size="small"
              >
                <v-icon start>mdi-web</v-icon>
                {{ t('marketplace.homepage') }}
              </v-btn>
            </div>
          </v-card-text>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<style scoped>
.plugin-detail {
  padding: 16px;
}

.plugin-icon-wrapper {
  width: 128px;
  height: 128px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--v-theme-surface);
  border-radius: 8px;
}
</style>
