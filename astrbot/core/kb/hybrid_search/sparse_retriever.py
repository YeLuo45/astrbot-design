"""Sparse Retriever using BM25 (rank_bm25)."""

from rank_bm25 import BM25Okapi
from typing import List, Tuple

from astrbot.core.kb.connectors.base import Document


class SparseRetriever:
    """Sparse retrieval using BM25 algorithm."""

    def __init__(self):
        """Initialize sparse retriever."""
        self.bm25: BM25Okapi = None
        self.documents: List[Document] = []

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the BM25 index.

        Args:
            documents: List of Document objects to index.
        """
        if not documents:
            return
        self.documents = documents
        tokenized = [doc.content.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Search for documents using BM25 sparse retrieval.

        Args:
            query: The search query.
            top_k: Number of results to return.

        Returns:
            List of (Document, score) tuples.
        """
        if self.bm25 is None:
            return []
        scores = self.bm25.get_scores(query.split())
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [
            (self.documents[i], float(s))
            for i, s in ranked[:top_k]
            if i < len(self.documents)
        ]
