"""Confluence connector for syncing Confluence pages and spaces."""

from typing import List, Optional

from astrbot.core.kb.connectors.base import BaseConnector, Document


class ConfluenceConnector(BaseConnector):
    """Connector for Atlassian Confluence."""

    def __init__(
        self,
        url: str,
        username: str,
        api_token: str,
        space_key: Optional[str] = None,
    ):
        """
        Initialize Confluence connector.

        Args:
            url: Confluence instance URL.
            username: Confluence username.
            api_token: Confluence API token.
            space_key: Optional specific space key to sync.
        """
        self.url = url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.space_key = space_key

    async def sync(self) -> List[Document]:
        """Synchronize pages from Confluence space(s)."""
        documents = []
        try:
            from atlassian import Confluence
        except ImportError:
            return documents

        try:
            confluence = Confluence(
                url=self.url,
                username=self.username,
                password=self.api_token,
            )

            if self.space_key:
                spaces = [self.space_key]
            else:
                spaces = self._get_spaces(confluence)

            for space in spaces:
                pages = confluence.get_all_pages_from_space(
                    space=space, expand="body.storage", limit=100
                )
                for page in pages:
                    content = self._extract_content(page)
                    documents.append(
                        Document(
                            id=str(page.get("id", "")),
                            content=content,
                            metadata={
                                "source": "confluence",
                                "space": space,
                                "title": page.get("title", ""),
                            },
                        )
                    )
        except Exception:
            pass
        return documents

    def _get_spaces(self, confluence) -> List[str]:
        """Get list of spaces to sync."""
        try:
            spaces = confluence.get_all_spaces(limit=50)
            return [s["key"] for s in spaces.get("results", [])]
        except Exception:
            return []

    def _extract_content(self, page: dict) -> str:
        """Extract text content from Confluence page."""
        body = page.get("body", {}).get("storage", {})
        return body.get("value", "")

    async def health_check(self) -> bool:
        """Check if Confluence is accessible."""
        try:
            from atlassian import Confluence
            confluence = Confluence(
                url=self.url, username=self.username, password=self.api_token
            )
            return confluence.get_all_spaces(limit=1) is not None
        except Exception:
            return False
