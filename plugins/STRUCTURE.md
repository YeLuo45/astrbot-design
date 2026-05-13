# Plugin Directory Structure

This document specifies the standard directory structure for AstrBot plugins in the marketplace.

## Plugin Package Format (.astrplug)

An `.astrplug` file is a `tar.gz` archive containing the plugin distribution.

```
my-plugin-1.0.0.astrplug/
├── manifest.json          # Required: Plugin metadata
├── star.json             # Required: Star plugin configuration
├── pyproject.toml        # Required: Python dependencies
├── astrbot_plugin/       # Required: Plugin source code
│   ├── __init__.py
│   └── ...
├── tests/                # Optional: Test files
├── README.md            # Optional: Plugin documentation
├── CHANGELOG.md         # Optional: Version history
└── assets/              # Optional: Static assets
```

## File Specifications

### manifest.json

```json
{
  "id": "uuid-v4",
  "slug": "plugin-unique-name",
  "name": "Plugin Display Name",
  "description": "Short description (max 200 characters)",
  "long_description": "Detailed description in Markdown",
  "version": "1.0.0",
  "author_id": "developer-uuid",
  "author_name": "Developer Name",
  "category": "ai|tools|integration|automation|other",
  "tags": ["tag1", "tag2"],
  "homepage": "https://example.com",
  "repository": "https://github.com/developer/plugin",
  "license": "MIT",
  "min_astrbot_version": "4.0.0",
  "manifest_version": 1
}
```

### star.json

Standard Star plugin configuration. See [Star Plugin System](../docs/plugin-development.md).

### pyproject.toml

```toml
[project]
name = "astrbot-plugin-name"
version = "1.0.0"
description = "Plugin description"
requires-python = ">=3.10"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
```

### Signature File (.signature)

Located alongside the `.astrplug` file in the release:
- Filename: `my-plugin-1.0.0.signature`
- Content: Ed25519 signature of the `.astrplug` file

### Developer Public Key

Stored in developer repository at:
```
.keys/
  {developer_id}_ed25519.pub
```

## Index Structure

The marketplace index (`index.json`) is hosted in the official marketplace repository:

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

## Hosting Requirements

1. **Official Marketplace Repository**: `astrbot/astrbot-marketplace`
2. **Index Location**: `https://raw.githubusercontent.com/astrbot/astrbot-marketplace/main/index.json`
3. **Plugin Releases**: Hosted on developer GitHub repositories via releases
4. **Public Key Storage**: Developer repositories under `.keys/` directory
