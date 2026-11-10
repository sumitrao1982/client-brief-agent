# Client Brief — Agentic Meeting-Prep Copilot for Investment Bankers

A sample **multi-agent** application: a banker logs in, opens a chat, names a client or ticker
("Prepare me for my meeting with Northwind Logistics"), and a team of agents built with
**Google ADK**, powered by **Claude**, researches the client **in parallel** from three kinds of source, then writes a meeting brief:

| Source | How it's implemented | What it gives the brief |
|---|---|---|
| **Internal research (RAG)** | ChromaDB vector store over internal PDFs | Our rating/PT, relationship history, contacts, open opportunities, sensitivities |
| **Latest market news** | Mock **Web Search MCP** server (stdio) | Recent headlines, activist / short-seller news, macro backdrop |
| **Financial data** | Mock **FactSet MCP** server (stdio) | Price, fundamentals, debt maturities, consensus, peers, ownership |

> ⚠️ All companies (Helix Biotherapeutics `HLXB`, Northwind Logistics `NWLG`, Aurora Renewable Power `AURP`),
> people, news and numbers are **fictitious** demo data.

---

## Architecture

> 📘 Full technical design, flows and RAG / ADK internals: [docs/DESIGN.md](docs/DESIGN.md)

```
React (Vite) ──SSE──► FastAPI ──► Google ADK Runner
  login + chat          /api/auth/login (JWT)
  live agent status     /api/chat/stream (Server-Sent Events)
  source citations      /api/rag/documents

ADK agent graph
client_brief_coordinator  (LlmAgent — talks to the banker)
 ├─ tools: resolve_company [FactSet MCP] · set_meeting_context · search_internal_research [RAG]
 └─ meeting_prep_pipeline (SequentialAgent)
      ├─ research_team (ParallelAgent — runs concurrently)
      │    ├─ internal_research_agent → search_internal_research → ChromaDB (PDF chunks)
      │    ├─ market_news_agent       → McpToolset(stdio) → mcp_servers/web_search_server.py
      │    └─ financial_data_agent    → McpToolset(stdio) → mcp_servers/factset_server.py
      └─ brief_writer_agent → combines the three outputs (via session state) into a Markdown brief
```

How it works:
1. The **coordinator** resolves the client through the FactSet MCP, saves `client_ticker` / `client_name` /
   `meeting_purpose` to session state, and hands off (`transfer_to_agent`) to the pipeline.
2. The **ParallelAgent** runs three specialists at the same time. Each writes its findings to state (`output_key`).
3. The **brief writer** reads those three state keys and produces the final brief, keeping every source citation
   (`[RAG: file p.N]`, `[Web: publisher, date]`, `[FactSet]`).
4. FastAPI streams every ADK event (agent start, tool call, tool result, messages) to the UI, which shows which agent
   is running, which MCP/RAG tool it called, and clickable citations that open the source PDF.
5. Follow-up questions go back to the coordinator, which keeps the conversation context.

## Which free RAG? → **ChromaDB** (used here)

| Option | Cost | Why / why not |
|---|---|---|
| **ChromaDB** ✅ | Free, open source (Apache-2.0) | Runs **embedded in the Python process**, no server, persists to disk, metadata filtering (filters by client ticker here), ships a **local embedding model** (all-MiniLM-L6-v2, ONNX) so **no embedding API key**. Best for a demo. |
| FAISS | Free | Very fast, but just an index: you handle persistence and metadata yourself. |
| Qdrant / Weaviate / Milvus | Free OSS (Docker) or free cloud tier | Good production choices; need a separate server. |
| pgvector | Free | Great if you already run Postgres. |
| Vertex AI RAG Engine | Paid (GCP) | Native ADK integration; consider for a production Google Cloud deployment. |

To switch later, only `backend/app/rag/store.py` needs to change.

## Project structure

```
client-brief-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app: auth, SSE chat, RAG document endpoints
│   │   ├── auth.py              # JWT auth with demo users
│   │   ├── chat_service.py      # ADK Runner + event → UI stream mapping
│   │   ├── config.py
│   │   ├── agents/agent.py      # ★ Google ADK multi-agent graph (root_agent)
│   │   ├── rag/store.py         # ChromaDB search
│   │   ├── rag/ingest.py        # PDF → chunks → ChromaDB
│   │   └── tools/rag_tool.py    # RAG exposed as an ADK tool
│   ├── mcp_servers/
│   │   ├── factset_server.py    # ★ mock FactSet MCP (6 tools)
│   │   ├── web_search_server.py # ★ mock Web Search MCP (2 tools)
│   │   └── mock_data/           # fictitious market data and news
│   ├── scripts/generate_sample_pdfs.py  # builds the internal PDFs
│   ├── data/internal_docs/      # 7 sample internal PDFs (research notes, coverage memos, sector outlook)
│   ├── requirements.txt
│   └── .env.example
└── frontend/                    # React + Vite
    └── src/ (App.jsx, api.js, components/Login.jsx, Chat.jsx, AgentPanel.jsx, styles.css)
```

## Run it locally

**Prerequisites:** Python 3.11+ (tested with 3.13), Node 18+ (tested with 22), and an Anthropic API key from
https://console.anthropic.com/ (Settings → API keys; usage is billed per token).

### 1. Backend

```bash
cd backend
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
# edit .env and set ANTHROPIC_API_KEY=...
python -m app.rag.ingest      # builds the ChromaDB index (first run downloads an ~80 MB embedding model)
uvicorn app.main:app --reload --port 8000
```

The backend also builds the index automatically at startup if it is empty. Health check: http://localhost:8000/api/health

### 2. Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in as **`banker` / `demo123`** (or `analyst` / `demo123`).

### Try these prompts
- *Prepare me for my meeting with Northwind Logistics tomorrow about refinancing their 2027 notes*
- *Brief me on HLXB — I am meeting their CFO next week*
- *I have a pitch to Aurora Renewable Power on a green hybrid bond. Get me ready.*
- Follow-up: *What should I avoid bringing up with the CEO?*

## Customising

- **Model:** Claude through ADK's `AnthropicLlm`. In `.env`, `CLAUDE_MODEL` (default `claude-opus-5-5`) runs the
  coordinator and brief writer. Set `CLAUDE_SPECIALIST_MODEL` (e.g. `claude-sonnet-5-5` or `claude-haiku-5-5`) to run
  the three research agents on a cheaper model. `CLAUDE_EFFORT` (default `medium`) sets how much Claude reasons.
  Each brief makes roughly 15–20 Claude calls; ADK prompt caching is enabled to cut the cost of repeated prompts.
- **Your own documents:** drop PDFs into `backend/data/internal_docs/` (name them `<TICKER>_...pdf`) and run
  `python -m app.rag.ingest` (or `POST /api/rag/reindex`). To add a ticker, also add it to the set in `rag/ingest.py → _doc_meta`.
- **Regenerate the sample PDFs:** `python scripts/generate_sample_pdfs.py`
- **Real MCP servers:** in `agents/agent.py`, swap the `_mcp_toolset("...py")` stdio params for the real server's
  `StreamableHTTPConnectionParams(url=...)` (or its stdio command). The agents' prompts stay the same.
- **Add a client to the mocks:** add entries in `mcp_servers/mock_data/factset_data.py` and `news_data.py`.

## Notes
- Sessions are stored in memory (`InMemorySessionService`). For persistence, use ADK's `DatabaseSessionService`.
- Auth uses hard-coded demo users. Replace it with your SSO/IdP before any real use.
