"""Runs the ADK agent graph and converts ADK events into UI-friendly stream events."""
import json
import logging
from typing import AsyncIterator

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.agent import root_agent

log = logging.getLogger(__name__)
APP_NAME = "client_brief"

AGENT_LABELS = {
    "client_brief_coordinator": "Coordinator Agent",
    "internal_research_agent": "Internal Research Agent",
    "market_news_agent": "Market News Agent",
    "financial_data_agent": "Financial Data Agent",
    "brief_writer_agent": "Brief Writer Agent",
}

RAG, FACTSET, WEB = "Internal Research RAG (ChromaDB)", "FactSet MCP (mock)", "Web Search MCP (mock)"
TOOL_SOURCES = {
    "search_internal_research": RAG,
    "resolve_company": FACTSET, "get_price_snapshot": FACTSET, "get_fundamentals": FACTSET,
    "get_consensus_estimates": FACTSET, "get_peer_comparison": FACTSET, "get_ownership": FACTSET,
    "search_news": WEB, "get_market_headlines": WEB,
    "set_meeting_context": "Session state",
    "transfer_to_agent": "Orchestration",
}
FINAL_AUTHORS = {"client_brief_coordinator", "brief_writer_agent"}


class ChatService:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=self.session_service)

    async def close(self):
        await self.runner.close()

    async def _ensure_session(self, user_id: str, session_id: str):
        session = await self.session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        if session is None:
            await self.session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    async def stream(self, user_id: str, session_id: str, message: str) -> AsyncIterator[dict]:
        await self._ensure_session(user_id, session_id)
        content = types.Content(role="user", parts=[types.Part(text=message)])
        started: set[str] = set()
        try:
            async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                author = event.author
                if author not in AGENT_LABELS:
                    continue
                if author not in started:
                    started.add(author)
                    yield {"type": "agent_start", "agent": author, "label": AGENT_LABELS[author]}

                for call in event.get_function_calls():
                    yield {"type": "tool_call", "agent": author, "tool": call.name,
                           "source": TOOL_SOURCES.get(call.name, "Tool"), "args": dict(call.args or {})}

                for resp in event.get_function_responses():
                    yield {"type": "tool_result", "agent": author, "tool": resp.name,
                           "source": TOOL_SOURCES.get(resp.name, "Tool"),
                           **_summarise(resp.name, resp.response)}

                text = "".join(p.text for p in (event.content.parts if event.content else []) if p.text and not p.thought)
                if text.strip() and not event.partial:
                    yield {"type": "message", "agent": author, "label": AGENT_LABELS[author],
                           "text": text, "final": author in FINAL_AUTHORS}
                    if author not in FINAL_AUTHORS:
                        yield {"type": "agent_done", "agent": author}
            yield {"type": "done"}
        except Exception as exc:  # surface model / key errors to the UI
            log.exception("Agent run failed")
            msg = str(exc)
            if "API key" in msg or "GOOGLE_API_KEY" in msg or "credentials" in msg.lower():
                msg = "LLM authentication failed — set GOOGLE_API_KEY in backend/.env. Details: " + msg
            yield {"type": "error", "message": msg[:800]}


def _payload(response) -> dict:
    """MCP tool responses arrive as {'content': [{'type': 'text', 'text': '<json>'}]}; unwrap them."""
    if not isinstance(response, dict):
        return {}
    if isinstance(response.get("structuredContent"), dict):
        return response["structuredContent"]
    content = response.get("content")
    if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
        try:
            return json.loads(content[0]["text"])
        except (ValueError, TypeError):
            return {"text": content[0]["text"]}
    return response


def _summarise(tool: str, response) -> dict:
    data = _payload(response)
    if tool == "search_internal_research":
        cites = [{"document": r.get("document"), "page": r.get("page"), "doc_type": r.get("doc_type"),
                  "relevance": r.get("relevance"), "excerpt": (r.get("text") or "")[:220]}
                 for r in data.get("results", [])]
        return {"summary": f"{len(cites)} passages retrieved from internal documents", "citations": cites}
    if tool in ("search_news", "get_market_headlines"):
        items = [{"title": r.get("title"), "publisher": r.get("publisher"), "date": r.get("published_date"),
                  "url": r.get("url")} for r in data.get("results", [])]
        return {"summary": f"{len(items)} articles found", "articles": items}
    if "error" in data:
        return {"summary": data["error"]}
    if tool == "resolve_company":
        return {"summary": f"Resolved to {data.get('name')} ({data.get('ticker')}) · {data.get('exchange')}"}
    if tool == "get_price_snapshot":
        return {"summary": f"{data.get('ticker')} last ${data.get('last')} ({data.get('change_pct_1d')}% 1D), "
                           f"mkt cap ${data.get('market_cap_mm')}M"}
    if tool == "transfer_to_agent":
        return {"summary": "Handing off to specialist agents"}
    keys = [k for k in data.keys() if k not in ("source", "as_of", "ticker")]
    return {"summary": "Returned: " + ", ".join(keys[:6]) if keys else "OK"}
