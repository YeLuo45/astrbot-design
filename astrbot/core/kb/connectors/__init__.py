"""Knowledge Base Connectors for external sources."""

from astrbot.core.kb.connectors.base import BaseConnector, Document
from astrbot.core.kb.connectors.notion_connector import NotionConnector
from astrbot.core.kb.connectors.obsidian_connector import ObsidianConnector
from astrbot.core.kb.connectors.confluence_connector import ConfluenceConnector

__all__ = [
    "BaseConnector",
    "Document",
    "NotionConnector",
    "ObsidianConnector",
    "ConfluenceConnector",
]
