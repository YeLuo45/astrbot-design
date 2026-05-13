"""Episodic Memory for storing and retrieving user interaction history."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

from astrbot.core.kb.connectors.base import Document


@dataclass
class Interaction:
    """Represents a single user interaction."""

    id: str
    user_id: str
    query: str
    response: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EpisodicMemory:
    """Long-term episodic memory for user interactions."""

    def __init__(self, vector_db, embedding_model):
        """
        Initialize episodic memory.

        Args:
            vector_db: Vector database with add() and search() methods.
            embedding_model: Model with async encode() method.
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.conversations: List[Interaction] = []

    async def store(self, interaction: Interaction) -> None:
        """
        Store an interaction in episodic memory.

        Args:
            interaction: The Interaction to store.
        """
        self.conversations.append(interaction)
        emb = await self.embedding_model.encode(
            f"{interaction.query} | {interaction.response}"
        )
        await self.vector_db.add(
            id=f"{interaction.user_id}:{interaction.id}",
            vector=emb,
            metadata={
                "query": interaction.query,
                "response": interaction.response,
                "timestamp": interaction.timestamp.isoformat(),
                "user_id": interaction.user_id,
            },
        )

    async def retrieve(
        self, user_id: str, query: str, limit: int = 5
    ) -> List[Interaction]:
        """
        Retrieve relevant interactions for a user based on a query.

        Args:
            user_id: The user ID.
            query: The search query.
            limit: Maximum number of results.

        Returns:
            List of relevant Interactions.
        """
        query_emb = await self.embedding_model.encode(query)
        results = await self.vector_db.search(vector=query_emb, top_k=limit)

        interactions = []
        for r in results:
            metadata = r.get("metadata", {})
            interactions.append(
                Interaction(
                    id=r.get("id", ""),
                    user_id=metadata.get("user_id", user_id),
                    query=metadata.get("query", ""),
                    response=metadata.get("response", ""),
                    timestamp=datetime.fromisoformat(
                        metadata.get("timestamp", datetime.now().isoformat())
                    ),
                )
            )
        return interactions
