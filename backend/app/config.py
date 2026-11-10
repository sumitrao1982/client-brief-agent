"""Central configuration loaded from environment variables / .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

# --- LLM (Google ADK) ---
# Default: Gemini via Google AI Studio (free tier). Set GOOGLE_API_KEY in .env.
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# --- RAG ---
DOCS_DIR = Path(os.getenv("DOCS_DIR", BACKEND_DIR / "data" / "internal_docs"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", BACKEND_DIR / "data" / "chroma"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "internal_research")

# --- MCP servers (mocked, launched over stdio) ---
MCP_DIR = BACKEND_DIR / "mcp_servers"

# --- Auth ---
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

# --- CORS ---
FRONTEND_ORIGINS = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")]
