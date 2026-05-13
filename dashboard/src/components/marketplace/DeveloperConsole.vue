<script setup lang="ts">
/**
 * DeveloperConsole.vue - For publishing plugins
 */
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const activeTab = ref('publish');

const pluginForm = ref({
  name: '',
  slug: '',
  description: '',
  longDescription: '',
  category: 'tools' as 'ai' | 'tools' | 'integration' | 'automation' | 'other',
  tags: [] as string[],
  homepage: '',
  repository: '',
  license: 'MIT',
  minAstrbotVersion: '4.0.0',
});

const tagInput = ref('');
const uploading = ref(false);
const uploadProgress = ref(0);
const error = ref('');
const success = ref('');

const categories = [
  { value: 'ai', title: 'AI' },
  { value: 'tools', title: 'Tools' },
  { value: 'integration', title: 'Integration' },
  { value: 'automation', title: 'Automation' },
  { value: 'other', title: 'Other' },
];

const licenses = [
  'MIT',
  'Apache-2.0',
  'GPL-3.0',
  'BSD-3-Clause',
  'MPL-2.0',
];

const addTag = () => {
  const tag = tagInput.value.trim().toLowerCase();
  if (tag && !pluginForm.value.tags.includes(tag) && pluginForm.value.tags.length < 5) {
    pluginForm.value.tags.push(tag);
  }
  tagInput.value = '';
};

const removeTag = (index: number) => {
  pluginForm.value.tags.splice(index, 1);
};

const generateSlug = () => {
  const name = pluginForm.value.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  pluginForm.value.slug = name;
};

const validateForm = () => {
  if (!pluginForm.value.name.trim()) return 'Plugin name is required';
  if (!pluginForm.value.slug.trim()) return 'Plugin slug is required';
  if (!pluginForm.value.description.trim()) return 'Description is required';
  if (pluginForm.value.description.length > 200) return 'Description must be 200 characters or less';
  return null;
};

const handlePublish = async () => {
  error.value = '';
  success.value = '';
  
  const validationError = validateForm();
  if (validationError) {
    error.value = validationError;
    return;
  }
  
  uploading.value = true;
  uploadProgress.value = 0;
  
  try {
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      uploadProgress.value += 10;
      if (uploadProgress.value >= 100) {
        clearInterval(progressInterval);
      }
    }, 200);
    
    // In real implementation, this would:
    // 1. Package the plugin as .astrplug
    // 2. Sign with developer's Ed25519 private key
    // 3. Upload to GitHub release assets
    // 4. Create/update PR to marketplace index
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    success.value = t('marketplace.publish_success');
    pluginForm.value = {
      name: '',
      slug: '',
      description: '',
      longDescription: '',
      category: 'tools',
      tags: [],
      homepage: '',
      repository: '',
      license: 'MIT',
      minAstrbotVersion: '4.0.0',
    };
  } catch (e) {
    error.value = t('marketplace.publish_failed');
  } finally {
    uploading.value = false;
    uploadProgress.value = 0;
  }
};

const myPlugins = ref([
  {
    id: '1',
    name: 'My ChatGPT Plugin',
    version: '1.2.0',
    status: 'approved',
    downloads: 150,
    rating: 4.5,
  },
]);
</script>

<template>
  <div class="developer-console">
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="publish">{{ t('marketplace.publish') }}</v-tab>
      <v-tab value="my-plugins">{{ t('marketplace.my_plugins') }}</v-tab>
    </v-tabs>

    <v-tabs-window v-model="activeTab">
      <!-- Publish Tab -->
      <v-tabs-window-item value="publish">
        <v-card variant="outlined">
          <v-card-title>{{ t('marketplace.publish_new_plugin') }}</v-card-title>
          <v-card-text>
            <v-alert type="info" variant="tonal" class="mb-4">
              {{ t('marketplace.publish_info') }}
            </v-alert>

            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="pluginForm.name"
                    :label="t('marketplace.plugin_name')"
                    variant="outlined"
                    @blur="generateSlug"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="pluginForm.slug"
                    :label="t('marketplace.plugin_slug')"
                    variant="outlined"
                    hint="URL-friendly name (lowercase, hyphens only)"
                    persistent-hint
                  />
                </v-col>
              </v-row>

              <v-textarea
                v-model="pluginForm.description"
                :label="t('marketplace.description')"
                variant="outlined"
                rows="2"
                counter
                maxlength="200"
              />

              <v-textarea
                v-model="pluginForm.longDescription"
                :label="t('marketplace.long_description')"
                variant="outlined"
                rows="4"
                :placeholder="t('marketplace.markdown_supported')"
              />

              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="pluginForm.category"
                    :items="categories"
                    :label="t('marketplace.category')"
                    variant="outlined"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="pluginForm.license"
                    :items="licenses"
                    :label="t('marketplace.license')"
                    variant="outlined"
                  />
                </v-col>
              </v-row>

              <!-- Tags -->
              <div class="mb-4">
                <div class="d-flex align-center">
                  <v-text-field
                    v-model="tagInput"
                    :label="t('marketplace.tags')"
                    variant="outlined"
                    density="compact"
                    @keyup.enter="addTag"
                  />
                  <v-btn class="ml-2" variant="tonal" @click="addTag">
                    {{ t('common.add') }}
                  </v-btn>
                </div>
                <div class="mt-2">
                  <v-chip
                    v-for="(tag, index) in pluginForm.tags"
                    :key="tag"
                    closable
                    size="small"
                    class="mr-2"
                    @click:close="removeTag(index)"
                  >
                    {{ tag }}
                  </v-chip>
                </div>
              </div>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="pluginForm.repository"
                    :label="t('marketplace.repository')"
                    variant="outlined"
                    placeholder="https://github.com/developer/plugin"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="pluginForm.homepage"
                    :label="t('marketplace.homepage')"
                    variant="outlined"
                  />
                </v-col>
              </v-row>

              <v-text-field
                v-model="pluginForm.minAstrbotVersion"
                :label="t('marketplace.min_version')"
                variant="outlined"
                style="max-width: 200px;"
              />

              <!-- File Upload Placeholder -->
              <v-alert type="warning" variant="tonal" class="mb-4">
                {{ t('marketplace.plugin_file_upload_note') }}
              </v-alert>
            </v-form>

            <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
              {{ error }}
            </v-alert>

            <v-alert v-if="success" type="success" variant="tonal" class="mb-4">
              {{ success }}
            </v-alert>

            <v-btn
              color="primary"
              size="large"
              :loading="uploading"
              @click="handlePublish"
            >
              {{ t('marketplace.publish') }}
            </v-btn>

            <v-progress-linear
              v-if="uploading"
              v-model="uploadProgress"
              class="mt-4"
              color="primary"
            />
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- My Plugins Tab -->
      <v-tabs-window-item value="my-plugins">
        <v-card variant="outlined">
          <v-card-title>{{ t('marketplace.my_plugins') }}</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>{{ t('marketplace.plugin_name') }}</th>
                  <th>{{ t('marketplace.version') }}</th>
                  <th>{{ t('marketplace.status') }}</th>
                  <th>{{ t('marketplace.downloads') }}</th>
                  <th>{{ t('marketplace.rating') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="plugin in myPlugins" :key="plugin.id">
                  <td>{{ plugin.name }}</td>
                  <td>v{{ plugin.version }}</td>
                  <td>
                    <v-chip
                      :color="plugin.status === 'approved' ? 'success' : 'warning'"
                      size="small"
                    >
                      {{ plugin.status }}
                    </v-chip>
                  </td>
                  <td>{{ plugin.downloads }}</td>
                  <td>{{ plugin.rating > 0 ? plugin.rating.toFixed(1) : '-' }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>
    </v-tabs>
  </div>
</template>

<style scoped>
.developer-console {
  padding: 16px;
}
</style>
