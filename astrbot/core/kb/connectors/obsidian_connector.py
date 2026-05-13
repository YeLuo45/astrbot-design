"""Obsidian vault connector for syncing markdown files."""

import glob
import os
from typing import List

from astrbot.core.kb.connectors.base import BaseConnector, Document


class ObsidianConnector(BaseConnector):
    """Connector for Obsidian vault."""

    def __init__(self, vault_path: str):
        """
        Initialize Obsidian connector.

        Args:
            vault_path: Path to the Obsidian vault directory.
        """
        self.vault_path = vault_path
        self.watcher = None

    async def sync(self) -> List[Document]:
        """Synchronize markdown files from Obsidian vault."""
        documents = []
        if not os.path.exists(self.vault_path):
            return documents

        pattern = os.path.join(self.vault_path, "**/*.md")
        md_files = glob.glob(pattern, recursive=True)

        for filepath in md_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                doc_id = os.path.relpath(filepath, self.vault_path)
                documents.append(
                    Document(
                        id=doc_id,
                        content=content,
                        metadata={
                            "source": "obsidian",
                            "filepath": filepath,
                            "vault_path": self.vault_path,
                        },
                    )
                )
            except Exception:
                continue
        return documents

    async def health_check(self) -> bool:
        """Check if vault path is accessible."""
        return os.path.isdir(self.vault_path)
