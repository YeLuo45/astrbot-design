<script setup lang="ts">
/**
 * Marketplace.vue - Plugin list with search/category/pagination
 */
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { marketplaceClient } from './marketplace';
import type { PluginEntry, PluginCategory, MarketplaceSearchResult } from './types';
import MarketplacePluginCard from './MarketplacePluginCard.vue';

const { t } = useI18n();

const plugins = ref<PluginEntry[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));

const searchQuery = ref('');
const selectedCategory = ref<PluginCategory | ''>('');
const selectedSort = ref<'downloads' | 'rating' | 'recent' | 'name'>('downloads');
const loading = ref(false);
const error = ref<string | null>(null);

const categories: { value: PluginCategory | ''; label: string }[] = [
  { value: '', label: 'All Categories' },
  { value: 'ai', label: 'AI' },
  { value: 'tools', label: 'Tools' },
  { value: 'integration', label: 'Integration' },
  { value: 'automation', label: 'Automation' },
  { value: 'other', label: 'Other' },
];

const sortOptions = [
  { value: 'downloads', label: 'Most Downloads' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'recent', label: 'Recently Updated' },
  { value: 'name', label: 'Name A-Z' },
];

const fetchPlugins = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result: MarketplaceSearchResult = await marketplaceClient.searchPlugins({
      query: searchQuery.value || undefined,
      category: selectedCategory.value || undefined,
      sort: selectedSort.value,
      page: currentPage.value,
      pageSize: pageSize.value,
    });
    
    plugins.value = result.plugins;
    total.value = result.total;
  } catch (e) {
    error.value = t('marketplace.error_loading');
    console.error('Failed to fetch plugins:', e);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchPlugins();
};

const handleCategoryChange = () => {
  currentPage.value = 1;
  fetchPlugins();
};

const handleSortChange = () => {
  currentPage.value = 1;
  fetchPlugins();
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchPlugins();
};

const handleInstallPlugin = (plugin: PluginEntry) => {
  // Emit event to parent or navigate to detail page
  console.log('Install plugin:', plugin.slug);
};

const handleOpenPlugin = (plugin: PluginEntry) => {
  // Navigate to plugin detail page
  console.log('Open plugin:', plugin.slug);
};

onMounted(() => {
  fetchPlugins();
});

// Debounce search
let searchTimeout: ReturnType<typeof setTimeout>;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    handleSearch();
  }, 300);
});
</script>

<template>
  <div class="marketplace">
    <!-- Search and Filters -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              :label="t('marketplace.search')"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @keyup.enter="handleSearch"
            />
          </v-col>
          
          <v-col cols="6" md="2">
            <v-select
              v-model="selectedCategory"
              :items="categories"
              :label="t('marketplace.category')"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="handleCategoryChange"
            />
          </v-col>
          
          <v-col cols="6" md="2">
            <v-select
              v-model="selectedSort"
              :items="sortOptions"
              :label="t('marketplace.sort_by')"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="handleSortChange"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Results -->
    <div v-if="loading" class="d-flex justify-center align-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="error" class="text-center py-8">
      <v-alert type="error" variant="tonal">{{ error }}</v-alert>
      <v-btn class="mt-4" @click="fetchPlugins">{{ t('common.retry') }}</v-btn>
    </div>

    <div v-else-if="plugins.length === 0" class="text-center py-8">
      <v-icon size="64" color="grey">mdi-plugin</v-icon>
      <div class="text-h6 mt-4">{{ t('marketplace.no_plugins') }}</div>
      <div class="text-body-2 text-grey">{{ t('marketplace.no_plugins_hint') }}</div>
    </div>

    <div v-else>
      <div class="d-flex justify-between align-center mb-4">
        <div class="text-body-2 text-grey">
          {{ t('marketplace.results_count', { count: total }) }}
        </div>
      </div>

      <v-row>
        <v-col
          v-for="plugin in plugins"
          :key="plugin.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <MarketplacePluginCard
            :plugin="plugin"
            @install="handleInstallPlugin"
            @open="handleOpenPlugin"
          />
        </v-col>
      </v-row>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="d-flex justify-center mt-6">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          :total-visible="7"
          @update:model-value="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.marketplace {
  padding: 16px;
}
</style>
