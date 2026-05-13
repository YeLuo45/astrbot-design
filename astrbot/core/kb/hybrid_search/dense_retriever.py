"""Dense Retriever using FAISS and sentence-transformers."""

import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict

from astrbot.core.kb.connectors.base import Document


class DenseRetriever:
    """Dense retrieval using FAISS index with sentence-transformers embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize dense retriever.

        Args:
            model_name: Name of the sentence-transformers model to use.
        """
        self.model = SentenceTransformer(model_name)
        dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(dim)
        self.documents: Dict[int, Document] = {}

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the FAISS index.

        Args:
            documents: List of Document objects to index.
        """
        if not documents:
            return
        embeddings = self.model.encode([doc.content for doc in documents])
        self.index.add(embeddings)
        for i, doc in enumerate(documents):
            self.documents[i] = doc

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Search for similar documents using dense embeddings.

        Args:
            query: The search query.
            top_k: Number of results to return.

        Returns:
            List of (Document, score) tuples.
        """
        query_emb = self.model.encode([query])
        distances, indices = self.index.search(query_emb, top_k)
        return [
            (self.documents[idx], float(dist))
            for idx, dist in zip(indices[0], distances[0])
            if idx >= 0 and idx in self.documents
        ]
