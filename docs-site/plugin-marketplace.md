# AstrBot Plugin Marketplace - Design Specification

> **Document Version**: 1.0  
> **Last Updated**: 2026-05-13

## Overview

The AstrBot Plugin Marketplace enables plugin discovery, installation, and management. This document describes the Phase 1 MVP architecture using a lightweight GitHub JSON + Actions approach.

## Architecture

### Phase 1: Lightweight Approach

```
┌─────────────────────────────────────────────────────┐
│                   Dashboard (Vue)                    │
├─────────────────────────────────────────────────────┤
│            Marketplace Client (JS)                   │
│         - Fetches index.json from GitHub            │
│         - Handles search/filter client-side         │
├─────────────────────────────────────────────────────┤
│     GitHub (astrbot/astrbot-marketplace)           │
│     - index.json (plugin registry)                  │
│     - Security scan reports                         │
├─────────────────────────────────────────────────────┤
│     Developer Repositories                           │
│     - Plugin releases (.astrplug)                   │
│     - Signature files (.signature)                  │
│     - Public keys (.keys/)                          │
└─────────────────────────────────────────────────────┘
```

No separate backend is required for Phase 1. All plugin metadata is stored in `index.json` hosted in the marketplace repository.

## Plugin Package Format

Plugins are distributed as `.astrplug` files (tar.gz archives):

```
my-plugin-1.0.0.astrplug/
├── manifest.json          # Plugin metadata
├── star.json             # Star plugin configuration
├── pyproject.toml        # Python dependencies
├── astrbot_plugin/       # Plugin source code
│   ├── __init__.py
│   └── ...
├── tests/               # Test files (optional)
├── README.md            # Documentation (optional)
└── assets/              # Static assets (optional)
```

### manifest.json

```json
{
  "id": "uuid-v4",
  "slug": "plugin-unique-name",
  "name": "Plugin Display Name",
  "description": "Short description (max 200 chars)",
  "version": "1.0.0",
  "author_id": "developer-uuid",
  "author_name": "Developer Name",
  "category": "ai|tools|integration|automation|other",
  "tags": ["tag1", "tag2"],
  "min_astrbot_version": "4.0.0"
}
```

## Index Structure

The `index.json` file contains all approved plugins:

```json
{
  "version": "1.0",
  "updated_at": "2026-05-13T00:00:00Z",
  "plugins": [
    {
      "id": "uuid",
      "slug": "plugin-slug",
      "name": "Plugin Name",
      "description": "Short description",
      "version": "1.0.0",
      "author_id": "developer-uuid",
      "author_name": "Developer Name",
      "category": "ai",
      "tags": ["tag1"],
      "download_url": "https://github.com/owner/repo/releases/download/v1.0.0/plugin-1.0.0.astrplug",
      "signature_url": "https://github.com/owner/repo/releases/download/v1.0.0/plugin-1.0.0.signature",
      "sha256": "abc123...",
      "min_astrbot_version": "4.0.0",
      "download_count": 100,
      "rating_average": 4.5,
      "rating_count": 10,
      "status": "approved",
      "created_at": "2026-05-01T00:00:00Z",
      "updated_at": "2026-05-13T00:00:00Z"
    }
  ]
}
```

## Security

### Plugin Signing (REQUIRED)

All plugins MUST be signed with Ed25519:

1. **Developer generates keypair**:
```bash
openssl genpkey -algorithm ED25519 -out private_key.pem
openssl pkey -in private_key.pem -pubout -out {developer_id}_ed25519.pub
```

2. **Developer signs plugin**:
```bash
tar -czf my-plugin-1.0.0.astrplug my-plugin/
openssl dgst -sha256 -sign private_key.pem my-plugin-1.0.0.astrplug > my-plugin-1.0.0.signature
```

3. **Verification in CI**:
```bash
openssl dgst -sha256 -verify developer_ed25519.pub -signature plugin.signature plugin.astrplug
```

### Security Scanning

GitHub Actions workflows run on each release:

| Check | Tool | Action on Failure |
|-------|------|-------------------|
| Malware Scan | ClamAV | Block release |
| Secret Detection | Custom patterns | Block release |
| Dependency Audit | pip-audit | Warning only |
| Permissions Check | find/chmod | Warning only |

## GitHub Actions Workflows

### scan-plugin.yml

Runs on release publication:
- Downloads plugin from release assets
- Extracts and scans with ClamAV
- Checks for sensitive files (passwords, keys, tokens)
- Audits Python dependencies
- Reports results as GitHub release comment

### verify-signature.yml

Manual workflow for signature verification:
- Takes plugin, signature, and public key paths as inputs
- Verifies Ed25519 signature
- Outputs verification report

## Dashboard Components

### Marketplace.vue

Main plugin listing page with:
- Search bar (debounced, 300ms)
- Category filter dropdown
- Sort options (downloads, rating, recent, name)
- Pagination
- Plugin cards grid

### PluginDetail.vue

Individual plugin page showing:
- Plugin icon and metadata
- Install button with loading state
- Download count, rating, version
- Full description
- Tags
- Links (repository, homepage)
- Minimum AstrBot version

### DeveloperConsole.vue

Developer-facing component for publishing:
- Plugin submission form
- File upload for .astrplug
- Tag management
- My Plugins tab showing submitted plugins

## API Reference

### Client-Side API (marketplace.ts)

```typescript
// Get marketplace index
const index = await marketplaceClient.getIndex();

// Search plugins
const results = await marketplaceClient.searchPlugins({
  query: 'chatgpt',
  category: 'ai',
  sort: 'downloads',
  page: 1,
  pageSize: 20,
});

// Get single plugin
const plugin = await marketplaceClient.getPlugin('chatgpt-integration');

// Check for updates
const updates = await marketplaceClient.checkUpdates(installedPlugins);

// Install plugin
const result = await marketplaceClient.installPlugin(plugin);
```

## Future Phases

### Phase 2
- Full FastAPI backend
- PostgreSQL for metadata
- Redis for caching
- User authentication
- Plugin ratings/reviews

### Phase 3
- Paid plugins with Stripe
- Developer revenue sharing
- Advanced analytics

## Hosting

- **Marketplace Repository**: `github.com/astrbot/astrbot-marketplace`
- **Index URL**: `https://raw.githubusercontent.com/astrbot/astrbot-marketplace/main/index.json`
- **Documentation**: `docs-site/plugin-marketplace.md`
