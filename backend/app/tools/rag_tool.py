"""ADK function tool that exposes the ChromaDB RAG store to agents."""
from app.rag import store

SOURCE = "Internal Research RAG (ChromaDB)"


def search_internal_research(query: str, ticker: str = "") -> dict:
    """Search the bank's INTERNAL research library (equity research notes, client coverage /
    relationship memos and sector outlooks) using semantic vector search (RAG).

    Args:
        query: what to look for, e.g. "relationship history and key contacts" or
            "financing needs and open opportunities".
        ticker: optional company ticker (e.g. "NWLG") to restrict results to that client.

    Returns:
        dict with matching passages, each citing its source document and page.
    """
    ticker = (ticker or "").strip().upper() or None
    if ticker:
        hits = store.search(query, ticker=ticker, top_k=4, include_sector=False)
        hits += store.search(query, ticker="SECTOR", top_k=1, include_sector=False)
    else:
        hits = store.search(query, top_k=5)
    if not hits:
        return {"source": SOURCE, "results": [],
                "note": "No internal documents found. Has the index been built (python -m app.rag.ingest)?"}
    return {"source": SOURCE, "query": query, "results": hits}
