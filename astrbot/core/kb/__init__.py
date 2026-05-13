"""
AstrBot Knowledge Base Module

Hybrid search combining dense (FAISS) and sparse (BM25) retrieval,
with Cross-Encoder reranking and LLM-based query expansion.
"""

from astrbot.core.kb.hybrid_search.dense_retriever import DenseRetriever
from astrbot.core.kb.hybrid_search.sparse_retriever import SparseRetriever
from astrbot.core.kb.hybrid_search.fusion import reciprocal_rank_fusion
from astrbot.core.kb.reranker import Reranker
from astrbot.core.kb.query_expander import QueryExpander
from astrbot.core.kb.episodic_memory import EpisodicMemory, Interaction
from astrbot.core.kb.connectors.base import BaseConnector, Document

__all__ = [
    "DenseRetriever",
    "SparseRetriever",
    "reciprocal_rank_fusion",
    "Reranker",
    "QueryExpander",
    "EpisodicMemory",
    "Interaction",
    "BaseConnector",
    "Document",
]
