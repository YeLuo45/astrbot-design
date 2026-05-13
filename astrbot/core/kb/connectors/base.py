"""Base connector and document types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Document:
    """Represents a document in the knowledge base."""

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstract base class for knowledge source connectors."""

    @abstractmethod
    async def sync(self) -> List[Document]:
        """
        Synchronize documents from the external source.

        Returns:
            List of Document objects.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the connector is healthy and can connect.

        Returns:
            True if healthy, False otherwise.
        """
        pass
