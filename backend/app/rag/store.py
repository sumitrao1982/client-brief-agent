"""ChromaDB-backed vector store for internal research documents.

ChromaDB runs embedded (no server) and uses its default local embedding model
(all-MiniLM-L6-v2 via ONNX), so the whole RAG stack is free and needs no API key.
"""
from functools import lru_cache

import chromadb

from app.config import CHROMA_COLLECTION, CHROMA_DIR


@lru_cache(maxsize=1)
def get_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def search(query: str, ticker: str | None = None, top_k: int = 5, include_sector: bool = True) -> list[dict]:
    """Semantic search over internal docs. If a ticker is given, restrict to that
    company's documents (plus cross-sector documents when include_sector=True)."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    where = None
    if ticker:
        tickers = [ticker.upper(), "SECTOR"] if include_sector else [ticker.upper()]
        where = {"ticker": {"$in": tickers}}
    res = collection.query(query_texts=[query], n_results=top_k, where=where)
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({
            "text": doc,
            "document": meta.get("source"),
            "doc_title": meta.get("title"),
            "doc_type": meta.get("doc_type"),
            "page": meta.get("page"),
            "ticker": meta.get("ticker"),
            "relevance": round(1 - float(dist), 3),
        })
    return hits
