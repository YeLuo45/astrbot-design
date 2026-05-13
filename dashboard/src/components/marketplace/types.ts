/**
 * Marketplace Types
 */

export interface PluginEntry {
  id: string;
  slug: string;
  name: string;
  description: string;
  version: string;
  author_id: string;
  author_name: string;
  category: PluginCategory;
  tags: string[];
  download_url: string;
  signature_url?: string;
  sha256: string;
  min_astrbot_version: string;
  download_count: number;
  rating_average: number;
  rating_count: number;
  homepage?: string;
  repository?: string;
  license?: string;
  status: PluginStatus;
  created_at: string;
  updated_at: string;
}

export type PluginCategory = 'ai' | 'tools' | 'integration' | 'automation' | 'other';
export type PluginStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'deleted';

export interface MarketplaceIndex {
  version: string;
  updated_at: string;
  plugins: PluginEntry[];
}

export interface PluginVersion {
  id: string;
  plugin_id: string;
  version: string;
  download_url: string;
  sha256: string;
  changelog: string;
  min_astrbot_version: string;
  created_at: string;
}

export interface InstalledPlugin {
  id: string;
  plugin_id: string;
  slug: string;
  name: string;
  version: string;
  installed_at: string;
  update_available?: string;
}

export interface ScanReport {
  plugin: string;
  scan_date: string;
  scanner_version: string;
  results: {
    clamav: { status: string };
    secrets: { status: string };
    pip_audit: { status: string };
    permissions: { status: string; suspicious_executables?: number };
  };
}

export interface SignatureVerification {
  verification_date: string;
  plugin_path: string;
  signature_path: string;
  public_key_path: string;
  algorithm: 'Ed25519';
  result: {
    valid: boolean;
    detail: string;
  };
}

export interface MarketplaceSearchParams {
  query?: string;
  category?: PluginCategory;
  tags?: string[];
  sort?: 'downloads' | 'rating' | 'recent' | 'name';
  page?: number;
  pageSize?: number;
}

export interface MarketplaceSearchResult {
  plugins: PluginEntry[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
