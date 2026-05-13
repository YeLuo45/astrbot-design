# Plugin Marketplace API Reference

> **API Version**: 1.0  
> **Last Updated**: 2026-05-13

## Overview

Phase 1 uses a lightweight approach with no backend server. The "API" is implemented as a JavaScript client that fetches `index.json` from GitHub and performs filtering/searching client-side.

## Index Endpoint

### GET Marketplace Index

Fetches the complete plugin registry.

**URL**: `https://raw.githubusercontent.com/astrbot/astrbot-marketplace/main/index.json`

**Method**: `GET`

**Response**:
```json
{
  "version": "1.0",
  "updated_at": "2026-05-13T00:00:00Z",
  "plugins": [...]
}
```

## JavaScript Client API

### `marketplaceClient.getIndex(forceRefresh?)`

Fetches the marketplace index.

**Parameters**:
- `forceRefresh` (boolean, optional): Skip cache and fetch fresh

**Returns**: `Promise<MarketplaceIndex>`

### `marketplaceClient.searchPlugins(params?)`

Search and filter plugins.

**Parameters**:
```typescript
interface MarketplaceSearchParams {
  query?: string;           // Search in name, description, tags
  category?: PluginCategory; // 'ai' | 'tools' | 'integration' | 'automation' | 'other'
  tags?: string[];         // Filter by tags
  sort?: 'downloads' | 'rating' | 'recent' | 'name';
  page?: number;
  pageSize?: number;
}
```

**Returns**: `Promise<MarketplaceSearchResult>`

### `marketplaceClient.getPlugin(slug)`

Get a single plugin by slug.

**Parameters**:
- `slug` (string): Plugin URL-friendly name

**Returns**: `Promise<PluginEntry | null>`

### `marketplaceClient.checkUpdates(installed)`

Check if installed plugins have updates available.

**Parameters**:
- `installed` (InstalledPlugin[]): List of installed plugins

**Returns**: `Promise<InstalledPlugin[]>` - Plugins with `update_available` field set

### `marketplaceClient.installPlugin(plugin)`

Install a plugin.

**Parameters**:
- `plugin` (PluginEntry): Plugin to install

**Returns**: `Promise<{ success: boolean; message: string }>`

## Data Types

### PluginEntry

```typescript
interface PluginEntry {
  id: string;                    // UUID v4
  slug: string;                  // URL-friendly name
  name: string;                  // Display name
  description: string;           // Short description (max 200 chars)
  version: string;               // Semantic version (x.y.z)
  author_id: string;             // Developer UUID
  author_name: string;           // Developer display name
  category: PluginCategory;
  tags: string[];
  download_url: string;          // Direct download URL for .astrplug
  signature_url?: string;         // Ed25519 signature URL
  sha256: string;                // SHA256 checksum
  min_astrbot_version: string;   // Minimum AstrBot version
  download_count: number;
  rating_average: number;        // 0-5
  rating_count: number;
  homepage?: string;
  repository?: string;
  license?: string;
  status: PluginStatus;
  created_at: string;           // ISO 8601
  updated_at: string;            // ISO 8601
}
```

### PluginCategory

```typescript
type PluginCategory = 'ai' | 'tools' | 'integration' | 'automation' | 'other';
```

### PluginStatus

```typescript
type PluginStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'deleted';
```

### MarketplaceSearchResult

```typescript
interface MarketplaceSearchResult {
  plugins: PluginEntry[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
```

## Error Handling

The client throws errors for network failures:

```typescript
try {
  const index = await marketplaceClient.getIndex();
} catch (error) {
  if (error.code === 'ECONNREFUSED') {
    // Network error
  } else if (error.response?.status === 404) {
    // Index not found
  }
}
```

## Caching

The client caches the index for 5 minutes to reduce API calls. Use `getIndex(true)` to force refresh.

## Rate Limiting

GitHub's raw content CDN has rate limits. For heavy usage, consider:
- Caching at the application level
- Using a proxy/caching server
- Implementing request batching
