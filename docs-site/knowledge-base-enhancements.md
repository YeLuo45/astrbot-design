# Knowledge Base Enhancements

> **PRD**: P-20260513-003  
> **Status**: Implemented

## Overview

This module provides enhanced knowledge base capabilities for AstrBot, combining multiple retrieval strategies with reranking and memory.

## Architecture

```
Query
  ├── Query Expander (LLM-based)
  │     └── Generate query reformulations
  ├── Hybrid Search
  │     ├── Dense Retriever (FAISS + sentence-transformers)
  │     └── Sparse Retriever (BM25)
  │     └── RRF Fusion
  └── Reranker (Cross-Encoder)
        └── Final ranking
```

## Components

### Hybrid Search

Combines dense (embedding-based) and sparse (BM25) retrieval using Reciprocal Rank Fusion.

**Dense Retriever**
- Uses `all-MiniLM-L6-v2` sentence-transformers model
- FAISS IndexFlatIP for fast similarity search
- Supports add_documents() and search() operations

**Sparse Retriever**
- Uses rank_bm25 (BM25Okapi)
- Token-based retrieval for keyword matching
- Complementary to dense retrieval

**Fusion**
- Weighted RRF: `score = w1*s1/(k+r1) + w2*s2/(k+r2)`
- Default weights: dense=0.6, sparse=0.4, k=60

### Reranker

Cross-Encoder model (`ms-marco-MiniLM-L-6-v2`) for precise relevance scoring:
- LRU cache (1000 entries) for performance
- Full reranking of candidates before final output

### Query Expander

LLM-based query reformulation:
- Generates up to 3 synonym variations
- Original query + expansions searched together

### Episodic Memory

User interaction history storage and retrieval:
- Stores queries and responses with timestamps
- Vector-based similarity search
- Per-user retrieval

### Connectors

External knowledge source integrations:

| Connector | Source | Features |
|-----------|--------|----------|
| NotionConnector | Notion API | Database/pages sync |
| ObsidianConnector | Local vault | Markdown file sync |
| ConfluenceConnector | Atlassian Confluence | Space/page sync |

## Usage Examples

### Basic Hybrid Search

```python
from astrbot.core.kb import (
    DenseRetriever, SparseRetriever, reciprocal_rank_fusion,
    Reranker, Document
)

# Initialize retrievers
dense = DenseRetriever("all-MiniLM-L6-v2")
sparse = SparseRetriever()

# Add documents
docs = [
    Document(id="1", content="Python tutorial"),
    Document(id="2", content="JavaScript guide"),
]
dense.add_documents(docs)
sparse.add_documents(docs)

# Search
dense_results = dense.search("python programming", top_k=10)
sparse_results = sparse.search("python programming", top_k=10)

# Fuse results
fused = reciprocal_rank_fusion(dense_results, sparse_results)

# Rerank
reranker = Reranker()
reranked = reranker.rerank("python programming", [d.content for d, _ in fused])
```

### Query Expansion

```python
from astrbot.core.kb import QueryExpander

expander = QueryExpander(llm_client)

# Expand query
expanded = await expander.expand("how to learn programming")
# Returns: ["how to learn programming", "best way to learn coding", ...]
```

### Episodic Memory

```python
from astrbot.core.kb import EpisodicMemory, Interaction
from datetime import datetime

memory = EpisodicMemory(vector_db, embedding_model)

# Store interaction
interaction = Interaction(
    id="123",
    user_id="user456",
    query="What is Python?",
    response="Python is a programming language.",
    timestamp=datetime.now()
)
await memory.store(interaction)

# Retrieve relevant memories
memories = await memory.retrieve("user456", "python", limit=5)
```

### Using Connectors

**Notion**
```python
from astrbot.core.kb.connectors import NotionConnector

notion = NotionConnector(
    api_key="secret_xxx",
    database_ids=["db_id_1", "db_id_2"]
)

# Sync documents
if await notion.health_check():
    docs = await notion.sync()
```

**Obsidian**
```python
from astrbot.core.kb.connectors import ObsidianConnector

obsidian = ObsidianConnector("/path/to/vault")
docs = await obsidian.sync()
```

## API Reference

### DenseRetriever

```python
DenseRetriever(model_name: str = "all-MiniLM-L6-v2")
```

| Method | Description |
|--------|-------------|
| `add_documents(documents: List[Document])` | Index documents |
| `search(query: str, top_k: int = 10)` | Search returns `List[Tuple[Document, float]]` |

### SparseRetriever

```python
SparseRetriever()
```

| Method | Description |
|--------|-------------|
| `add_documents(documents: List[Document])` | Build BM25 index |
| `search(query: str, top_k: int = 10)` | Search returns `List[Tuple[Document, float]]` |

### Reranker

```python
Reranker(model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", cache_size: int = 1000)
```

| Method | Description |
|--------|-------------|
| `rerank(query: str, candidates: List[str], top_k: int = 10)` | Returns re-ranked list |

### QueryExpander

```python
QueryExpander(llm)
```

| Method | Description |
|--------|-------------|
| `async expand(query: str, max_expansions: int = 3)` | Returns `List[str]` with original + expansions |

### EpisodicMemory

```python
EpisodicMemory(vector_db, embedding_model)
```

| Method | Description |
|--------|-------------|
| `async store(interaction: Interaction)` | Store interaction |
| `async retrieve(user_id: str, query: str, limit: int = 5)` | Returns `List[Interaction]` |

## Configuration

```yaml
knowledge_base:
  hybrid_search:
    enabled: true
    dense_weight: 0.6
    sparse_weight: 0.4
    fusion: "rrf"
    rrf_k: 60

  reranker:
    enabled: true
    model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: 10

  query_expansion:
    enabled: false
    max_expansions: 3

  connectors:
    notion:
      enabled: false
      api_key: "${NOTION_API_KEY}"
      database_ids: []

    obsidian:
      enabled: false
      vault_path: "/path/to/vault"

    confluence:
      enabled: false
      url: "https://company.atlassian.net"
      username: "${CONFLUENCE_USER}"
      api_token: "${CONFLUENCE_TOKEN}"

  episodic_memory:
    enabled: false
    retention_days: 90
    max_memories_per_user: 1000
```

## Dependencies

```
faiss-cpu>=1.7.4
rank_bm25>=0.2.2
sentence-transformers>=2.2.2
cross-encoder>=0.1.0
notion-client>=2.0.0
atlassian>=1.0.0
```

## Testing Locally

```bash
# Install dependencies
pip install faiss-cpu rank_bm25 sentence-transformers cross-encoder

# Run syntax check on all KB modules
python -m py_compile astrbot/core/kb/__init__.py
python -m py_compile astrbot/core/kb/hybrid_search/*.py
python -m py_compile astrbot/core/kb/reranker.py
python -m py_compile astrbot/core/kb/query_expander.py
python -m py_compile astrbot/core/kb/episodic_memory.py
python -m py_compile astrbot/core/kb/connectors/*.py

# Run unit tests (if available)
pytest tests/unit/test_sparse_retriever.py -v
pytest tests/unit/test_faiss_vec_db.py -v
```

## File Structure

```
astrbot/core/kb/
├── __init__.py
├── hybrid_search/
│   ├── __init__.py
│   ├── dense_retriever.py
│   ├── sparse_retriever.py
│   └── fusion.py
├── reranker.py
├── query_expander.py
├── episodic_memory.py
└── connectors/
    ├── __init__.py
    ├── base.py
    ├── notion_connector.py
    ├── obsidian_connector.py
    └── confluence_connector.py
```
