"""Notion connector for syncing Notion pages and databases."""

from typing import List

from notion_client import AsyncClient

from astrbot.core.kb.connectors.base import BaseConnector, Document


class NotionConnector(BaseConnector):
    """Connector for Notion workspace."""

    def __init__(self, api_key: str, database_ids: List[str] = None):
        """
        Initialize Notion connector.

        Args:
            api_key: Notion API token.
            database_ids: List of database IDs to sync.
        """
        self.client = AsyncClient(auth=api_key)
        self.database_ids = database_ids or []

    async def sync(self) -> List[Document]:
        """Synchronize pages from Notion databases."""
        documents = []
        for db_id in self.database_ids:
            try:
                results = await self.client.databases.query(db_id)
                for page in results.get("results", []):
                    content = self._page_to_text(page)
                    documents.append(
                        Document(
                            id=page["id"],
                            content=content,
                            metadata={"source": "notion", "database_id": db_id},
                        )
                    )
            except Exception:
                continue
        return documents

    def _page_to_text(self, page: dict) -> str:
        """Convert Notion page properties to text."""
        props = page.get("properties", {})
        parts = []
        for key, value in props.items():
            if isinstance(value, dict):
                # Handle common Notion property types
                if "title" in value:
                    parts.append(str(value["title"]))
                elif "rich_text" in value:
                    parts.append(str(value["rich_text"]))
                elif "number" in value:
                    parts.append(str(value["number"]))
                else:
                    parts.append(str(value))
            else:
                parts.append(str(value))
        return " ".join(parts)

    async def health_check(self) -> bool:
        """Check if Notion API is accessible."""
        try:
            await self.client.users.me()
            return True
        except Exception:
            return False
