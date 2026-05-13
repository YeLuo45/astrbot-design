"""Score fusion using Reciprocal Rank Fusion (RRF)."""

from typing import List, Tuple, Dict

from astrbot.core.kb.connectors.base import Document


def reciprocal_rank_fusion(
    dense_results: List[Tuple[Document, float]],
    sparse_results: List[Tuple[Document, float]],
    k: int = 60,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[Tuple[Document, float]]:
    """
    Fuse dense and sparse retrieval results using weighted Reciprocal Rank Fusion.

    Args:
        dense_results: Results from dense retriever (Document, score).
        sparse_results: Results from sparse retriever (Document, score).
        k: RRF smoothing parameter.
        dense_weight: Weight for dense retrieval scores.
        sparse_weight: Weight for sparse retrieval scores.

    Returns:
        Combined and re-ranked list of (Document, score) tuples.
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    # Process dense results
    for rank, (doc, score) in enumerate(dense_results):
        doc_id = doc.id
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0) + (dense_weight * score) / (k + rank + 1)

    # Process sparse results
    for rank, (doc, score) in enumerate(sparse_results):
        doc_id = doc.id
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0) + (sparse_weight * score) / (k + rank + 1)

    # Sort by combined score
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(doc_map[doc_id], score) for doc_id, score in sorted_results]
