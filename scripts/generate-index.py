#!/usr/bin/env python3
"""
Generate or update the marketplace index.json file.

This script aggregates plugin information from registered developer repositories
and generates the marketplace index.json file.

Usage:
    python generate-index.py --output index.json
    python generate-index.py --update --input index.json --plugin-dir ./plugins
"""

import argparse
import json
import os
import sys
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MARKETPLACE_REPO = "astrbot/astrbot-marketplace"
MARKETPLACE_INDEX_URL = f"https://raw.githubusercontent.com/{MARKETPLACE_REPO}/main/index.json"


def compute_sha256(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def fetch_json(url: str) -> dict:
    """Fetch JSON from a URL."""
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode())


def create_plugin_entry(
    plugin_id: str,
    slug: str,
    name: str,
    description: str,
    version: str,
    author_id: str,
    author_name: str,
    category: str,
    tags: list,
    download_url: str,
    signature_url: Optional[str],
    sha256: str,
    min_astrbot_version: str,
    repository: Optional[str] = None,
    homepage: Optional[str] = None,
    license: Optional[str] = None,
) -> dict:
    """Create a standardized plugin entry."""
    now = datetime.now(timezone.utc).isoformat()
    
    return {
        "id": plugin_id,
        "slug": slug,
        "name": name,
        "description": description[:200] if description else "",  # Max 200 chars
        "version": version,
        "author_id": author_id,
        "author_name": author_name,
        "category": category,
        "tags": tags[:5] if tags else [],  # Max 5 tags
        "download_url": download_url,
        "signature_url": signature_url,
        "sha256": sha256,
        "min_astrbot_version": min_astrbot_version,
        "download_count": 0,
        "rating_average": 0.0,
        "rating_count": 0,
        "repository": repository,
        "homepage": homepage,
        "license": license,
        "status": "approved",
        "created_at": now,
        "updated_at": now,
    }


def update_existing_entry(existing: dict, updates: dict) -> dict:
    """Update an existing plugin entry with new information."""
    # Keep existing download count and ratings
    preserved_fields = ["download_count", "rating_average", "rating_count", "created_at"]
    
    for field in preserved_fields:
        if field in existing and field in updates:
            updates[field] = existing[field]
    
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    return updates


def generate_index(
    plugins: list,
    output_path: Optional[str] = None,
    input_path: Optional[str] = None
) -> dict:
    """
    Generate marketplace index from plugin list.
    
    Args:
        plugins: List of plugin entries
        output_path: Path to write index.json
        input_path: Optional path to existing index.json for preserving stats
    
    Returns:
        The generated index dictionary
    """
    # Load existing index if provided
    existing_plugins = {}
    if input_path and os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            existing_index = json.load(f)
            for plugin in existing_index.get("plugins", []):
                existing_plugins[plugin["slug"]] = plugin
    
    # Update or add plugins
    final_plugins = []
    for plugin in plugins:
        slug = plugin["slug"]
        if slug in existing_plugins:
            # Update existing, preserving stats
            updated = update_existing_entry(existing_plugins[slug], plugin)
            final_plugins.append(updated)
        else:
            final_plugins.append(plugin)
    
    # Sort by download count (descending)
    final_plugins.sort(key=lambda p: p.get("download_count", 0), reverse=True)
    
    # Create index structure
    index = {
        "version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "plugins": final_plugins,
    }
    
    # Write output
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"Index written to {output_path}")
        print(f"Total plugins: {len(final_plugins)}")
    
    return index


def main():
    parser = argparse.ArgumentParser(description="Generate marketplace index.json")
    parser.add_argument(
        "--output", "-o",
        help="Output path for index.json"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input path to existing index.json (for preserving stats)"
    )
    parser.add_argument(
        "--plugin-dir",
        help="Directory containing plugin manifest.json files"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing index.json"
    )
    
    args = parser.parse_args()
    
    if args.validate and args.input:
        # Validation mode
        with open(args.input, "r", encoding="utf-8") as f:
            index = json.load(f)
        
        errors = []
        for i, plugin in enumerate(index.get("plugins", [])):
            # Required fields check
            required = ["id", "slug", "name", "description", "version", "download_url", "sha256"]
            for field in required:
                if field not in plugin:
                    errors.append(f"Plugin {i}: missing required field '{field}'")
            
            # Slug format check
            if "slug" in plugin and not plugin["slug"].replace("-", "").isalnum():
                errors.append(f"Plugin {plugin.get('slug')}: invalid slug format")
        
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print(f"Validation passed. {len(index.get('plugins', []))} plugins.")
    
    elif args.plugin_dir:
        # Generate from plugin directory
        plugins = []
        plugin_dir = Path(args.plugin_dir)
        
        for manifest_path in plugin_dir.rglob("manifest.json"):
            # Read manifest
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            # Get related file paths
            plugin_dir_path = manifest_path.parent
            astrplug_files = list(plugin_dir_path.glob("*.astrplug"))
            
            if astrplug_files:
                latest_astrplug = max(astrplug_files, key=lambda p: p.stat().st_mtime)
                signature_path = latest_astrplug.with_suffix(".signature")
                
                download_url = f"file://{latest_astrplug.absolute()}"
                signature_url = f"file://{signature_path.absolute()}" if signature_path.exists() else None
                sha256 = compute_sha256(str(latest_astrplug))
                
                plugin_entry = create_plugin_entry(
                    plugin_id=manifest.get("id", ""),
                    slug=manifest.get("slug", ""),
                    name=manifest.get("name", ""),
                    description=manifest.get("description", ""),
                    version=manifest.get("version", "1.0.0"),
                    author_id=manifest.get("author_id", ""),
                    author_name=manifest.get("author_name", ""),
                    category=manifest.get("category", "other"),
                    tags=manifest.get("tags", []),
                    download_url=download_url,
                    signature_url=signature_url,
                    sha256=sha256,
                    min_astrbot_version=manifest.get("min_astrbot_version", "4.0.0"),
                    repository=manifest.get("repository"),
                    homepage=manifest.get("homepage"),
                    license=manifest.get("license"),
                )
                plugins.append(plugin_entry)
        
        generate_index(plugins, args.output, args.input)
    
    elif args.output:
        # Just create empty index or update timestamp
        index = {
            "version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "plugins": [],
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"Empty index written to {args.output}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
