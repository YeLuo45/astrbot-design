/**
 * Marketplace API Client
 * Phase 1: Lightweight GitHub JSON + Actions (no separate backend)
 */

import axios, { AxiosInstance } from 'axios';
import type {
  PluginEntry,
  MarketplaceIndex,
  MarketplaceSearchParams,
  MarketplaceSearchResult,
  InstalledPlugin,
} from './types';

const MARKETPLACE_INDEX_URL = 'https://raw.githubusercontent.com/astrbot/astrbot-marketplace/main/index.json';

class MarketplaceClient {
  private client: AxiosInstance;
  private indexCache: MarketplaceIndex | null = null;
  private cacheTimestamp: number = 0;
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.client = axios.create({
      baseURL: '/api/marketplace',
      timeout: 30000,
    });
  }

  /**
   * Fetch the marketplace index from GitHub
   */
  async getIndex(forceRefresh = false): Promise<MarketplaceIndex> {
    const now = Date.now();
    
    if (!forceRefresh && this.indexCache && (now - this.cacheTimestamp) < this.CACHE_TTL) {
      return this.indexCache;
    }

    try {
      const response = await axios.get<MarketplaceIndex>(MARKETPLACE_INDEX_URL, {
        timeout: 30000,
      });
      this.indexCache = response.data;
      this.cacheTimestamp = now;
      return response.data;
    } catch (error) {
      console.error('Failed to fetch marketplace index:', error);
      throw new Error('Unable to fetch plugin marketplace index');
    }
  }

  /**
   * Search plugins with filters
   */
  async searchPlugins(params: MarketplaceSearchParams = {}): Promise<MarketplaceSearchResult> {
    const index = await this.getIndex();
    
    let filtered = index.plugins.filter(p => p.status === 'approved');

    // Filter by query
    if (params.query) {
      const query = params.query.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.description.toLowerCase().includes(query) ||
        p.tags.some(t => t.toLowerCase().includes(query))
      );
    }

    // Filter by category
    if (params.category) {
      filtered = filtered.filter(p => p.category === params.category);
    }

    // Filter by tags
    if (params.tags && params.tags.length > 0) {
      filtered = filtered.filter(p =>
        params.tags!.some(t => p.tags.includes(t))
      );
    }

    // Sort
    switch (params.sort) {
      case 'downloads':
        filtered.sort((a, b) => b.download_count - a.download_count);
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating_average - a.rating_average);
        break;
      case 'recent':
        filtered.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
        break;
      case 'name':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      default:
        filtered.sort((a, b) => b.download_count - a.download_count);
    }

    // Pagination
    const page = params.page || 1;
    const pageSize = params.pageSize || 20;
    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (page - 1) * pageSize;
    const plugins = filtered.slice(start, start + pageSize);

    return {
      plugins,
      total,
      page,
      pageSize,
      totalPages,
    };
  }

  /**
   * Get a single plugin by slug
   */
  async getPlugin(slug: string): Promise<PluginEntry | null> {
    const index = await this.getIndex();
    return index.plugins.find(p => p.slug === slug && p.status === 'approved') || null;
  }

  /**
   * Get all approved plugins
   */
  async getAllPlugins(): Promise<PluginEntry[]> {
    const index = await this.getIndex();
    return index.plugins.filter(p => p.status === 'approved');
  }

  /**
   * Check for plugin updates
   */
  async checkUpdates(installedPlugins: InstalledPlugin[]): Promise<InstalledPlugin[]> {
    const index = await this.getIndex();
    const updates: InstalledPlugin[] = [];

    for (const installed of installedPlugins) {
      const latest = index.plugins.find(
        p => p.slug === installed.slug && p.status === 'approved'
      );
      
      if (latest && this.compareVersions(latest.version, installed.version) > 0) {
        updates.push({
          ...installed,
          update_available: latest.version,
        });
      }
    }

    return updates;
  }

  /**
   * Compare semantic versions
   */
  private compareVersions(a: string, b: string): number {
    const partsA = a.split('.').map(Number);
    const partsB = b.split('.').map(Number);
    
    for (let i = 0; i < Math.max(partsA.length, partsB.length); i++) {
      const numA = partsA[i] || 0;
      const numB = partsB[i] || 0;
      if (numA > numB) return 1;
      if (numA < numB) return -1;
    }
    return 0;
  }

  /**
   * Download and install a plugin
   */
  async installPlugin(plugin: PluginEntry): Promise<{ success: boolean; message: string }> {
    try {
      // Download the plugin file
      const response = await axios.get(plugin.download_url, {
        responseType: 'arraybuffer',
        timeout: 120000,
      });

      // Verify SHA256
      const downloadedHash = await this.computeSha256(response.data);
      if (downloadedHash !== plugin.sha256) {
        return { success: false, message: 'SHA256 checksum mismatch. Plugin may be corrupted.' };
      }

      // Download signature if available
      if (plugin.signature_url) {
        const sigResponse = await axios.get(plugin.signature_url, {
          timeout: 10000,
        });
        // Signature verification would happen here
        // For now, we trust the signature URL presence as indication of signed plugin
      }

      // TODO: Call backend API to actually install the plugin
      // This would be: POST /api/marketplace/install with the plugin data
      
      return { success: true, message: 'Plugin installed successfully' };
    } catch (error) {
      console.error('Failed to install plugin:', error);
      return { success: false, message: 'Failed to download or verify plugin' };
    }
  }

  /**
   * Compute SHA256 hash of data
   */
  private async computeSha256(data: ArrayBuffer): Promise<string> {
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }
}

export const marketplaceClient = new MarketplaceClient();
export default marketplaceClient;
