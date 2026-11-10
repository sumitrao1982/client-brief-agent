"""FastAPI entrypoint for the Client Brief agentic application.

Run (from backend/):  uvicorn app.main:app --reload --port 8000
"""
import json
import logging
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.auth import authenticate, create_token, current_user, current_user_header_or_query
from app.chat_service import ChatService
from app.config import ADK_MODEL, DOCS_DIR, FRONTEND_ORIGINS
from app.rag.ingest import ingest
from app.rag.store import get_collection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("client_brief")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if get_collection().count() == 0:
        log.info("RAG index empty — ingesting internal PDFs...")
        ingest()
    app.state.chat = ChatService()
    yield
    await app.state.chat.close()


app = FastAPI(title="Client Brief Agent API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=1, max_length=100)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": ADK_MODEL, "rag_chunks": get_collection().count()}


@app.post("/api/auth/login")
def login(body: LoginRequest):
    user = authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_token(user), "token_type": "bearer", "user": user}


@app.get("/api/auth/me")
def me(user: dict = Depends(current_user)):
    return user


@app.post("/api/chat/stream")
async def chat_stream(body: ChatRequest, user: dict = Depends(current_user)):
    """Server-Sent Events stream of agent activity + messages."""
    service: ChatService = app.state.chat

    async def gen():
        async for evt in service.stream(user["username"], body.session_id, body.message):
            yield f"data: {json.dumps(evt, default=str)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/rag/documents")
def list_documents(user: dict = Depends(current_user)):
    """Documents in the RAG knowledge base, with chunk counts."""
    metas = get_collection().get(include=["metadatas"])["metadatas"]
    counts = Counter(m["source"] for m in metas)
    info = {m["source"]: m for m in metas}
    return [{"document": name, "title": info[name].get("title"), "doc_type": info[name].get("doc_type"),
             "ticker": info[name].get("ticker"), "chunks": n} for name, n in sorted(counts.items())]


@app.get("/api/rag/documents/{name}")
def get_document(name: str, user: dict = Depends(current_user_header_or_query)):
    path = (DOCS_DIR / name).resolve()
    if path.parent != DOCS_DIR.resolve() or path.suffix.lower() != ".pdf" or not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(path, media_type="application/pdf", filename=name,
                        content_disposition_type="inline")


@app.post("/api/rag/reindex")
def reindex(user: dict = Depends(current_user)):
    return {"chunks": ingest()}
