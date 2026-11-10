"""Ingest PDFs from data/internal_docs into ChromaDB.

Usage (from backend/):
    python -m app.rag.ingest            # (re)build the index
"""
import re

from pypdf import PdfReader

from app.config import DOCS_DIR
from app.rag.store import get_collection

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


FOOTER_RE = re.compile(r"Meridian Capital Partners — INTERNAL / CONFIDENTIAL — SAMPLE DOCUMENT.*?Page \d+", re.S)


def _clean(text: str) -> str:
    text = FOOTER_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _chunks(text: str):
    text = _clean(text)
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        if end < len(text):  # try not to cut mid-sentence
            cut = text.rfind(". ", start + CHUNK_SIZE // 2, end)
            if cut != -1:
                end = cut + 1
        yield text[start:end].strip()
        if end >= len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
        space = text.find(" ", start)  # begin the next chunk on a word boundary
        if space != -1 and space - start < 40:
            start = space + 1


def _doc_meta(filename: str) -> dict:
    prefix = filename.split("_")[0].upper()
    ticker = prefix if prefix in {"HLXB", "NWLG", "AURP"} else "SECTOR"
    if "Research_Note" in filename:
        doc_type = "Equity Research Note"
    elif "Coverage" in filename:
        doc_type = "Coverage / Relationship Memo"
    else:
        doc_type = "Sector Outlook"
    return {"ticker": ticker, "doc_type": doc_type}


def ingest() -> int:
    collection = get_collection()
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids, docs, metas = [], [], []
    pdfs = sorted(DOCS_DIR.glob("*.pdf"))
    for pdf in pdfs:
        reader = PdfReader(str(pdf))
        title = (reader.metadata.title if reader.metadata else None) or pdf.stem
        base = _doc_meta(pdf.name)
        for page_no, page in enumerate(reader.pages, start=1):
            for i, chunk in enumerate(_chunks(page.extract_text() or "")):
                if len(chunk) < 40:
                    continue
                ids.append(f"{pdf.stem}-p{page_no}-c{i}")
                docs.append(chunk)
                metas.append({**base, "source": pdf.name, "title": title, "page": page_no})
        print(f"  indexed {pdf.name}")

    if ids:
        collection.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Ingested {len(ids)} chunks from {len(pdfs)} PDFs into ChromaDB.")
    return len(ids)


if __name__ == "__main__":
    ingest()
