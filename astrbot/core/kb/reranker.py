"""Reranker using Cross-Encoder with LRU caching."""

from functools import lru_cache
from sentence_transformers import CrossEncoder
from typing import List
import hashlib


class Reranker:
    """Cross-Encoder based reranker with LRU cache for improved performance."""

    def __init__(
        self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", cache_size: int = 1000
    ):
        """
        Initialize reranker.

        Args:
            model_name: Name of the Cross-Encoder model.
            cache_size: Maximum number of entries in the LRU cache.
        """
        self.model = CrossEncoder(model_name)
        self._cache_size = cache_size

    def _make_key(self, query: str, doc: str) -> str:
        """Generate a cache key for a query-document pair."""
        return hashlib.md5(f"{query}|{doc}".encode()).hexdigest()

    @lru_cache(maxsize=1000)
    def _score_cached(self, query: str, doc: str) -> float:
        """Score a single query-document pair (cached)."""
        return float(self.model.predict([(query, doc)])[0])

    def rerank(self, query: str, candidates: List[str], top_k: int = 10) -> List[str]:
        """
        Rerank candidate documents using Cross-Encoder scores.

        Args:
            query: The search query.
            candidates: List of candidate document contents.
            top_k: Number of top results to return.

        Returns:
            Re-ranked list of document contents.
        """
        if not candidates:
            return []

        # Score all candidates
        scored = []
        for doc in candidates:
            try:
                score = self._score_cached(query, doc)
            except Exception:
                # Fallback: assign neutral score on error
                score = 0.0
            scored.append((doc, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]
