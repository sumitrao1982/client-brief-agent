"""Central configuration loaded from environment variables / .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

# --- LLM: Claude via the Anthropic API (used by Google ADK's AnthropicLlm) ---
# Needs ANTHROPIC_API_KEY in .env (https://console.anthropic.com/).
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
# Model for the three research specialists; defaults to CLAUDE_MODEL.
# Set e.g. claude-sonnet-5-5 or claude-haiku-5-5 here to cut cost.
CLAUDE_SPECIALIST_MODEL = os.getenv("CLAUDE_SPECIALIST_MODEL", CLAUDE_MODEL)
# Reasoning effort: low | medium | high | xhigh | max (Claude Opus 5.5's default is medium).
CLAUDE_EFFORT = os.getenv("CLAUDE_EFFORT", "medium")
CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "16000"))

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
