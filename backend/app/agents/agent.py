"""Google ADK multi-agent graph for the Client Brief application.

    client_brief_coordinator  (LlmAgent, root — talks to the banker)
      ├─ tools: resolve_company [FactSet MCP], set_meeting_context, search_internal_research [RAG]
      └─ meeting_prep_pipeline  (SequentialAgent)
           ├─ research_team  (ParallelAgent — runs concurrently)
           │    ├─ internal_research_agent  → ChromaDB RAG over internal PDFs
           │    ├─ market_news_agent        → Web Search MCP (mock, stdio)
           │    └─ financial_data_agent     → FactSet MCP (mock, stdio)
           └─ brief_writer_agent  → synthesises the final meeting brief
"""
import sys
from datetime import date

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

from app.config import ADK_MODEL, MCP_DIR
from app.tools.rag_tool import search_internal_research

GEN_CONFIG = types.GenerateContentConfig(temperature=0.2)


# ---------------------------------------------------------------------------
# MCP toolsets (each spawns the mock server as a stdio subprocess)
# ---------------------------------------------------------------------------
def _mcp_toolset(script: str, tool_filter: list[str] | None = None) -> McpToolset:
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command=sys.executable, args=[str(MCP_DIR / script)]),
            timeout=30,
        ),
        tool_filter=tool_filter,
    )


# ---------------------------------------------------------------------------
# Coordinator tool: store the resolved client in session state
# ---------------------------------------------------------------------------
def set_meeting_context(ticker: str, company_name: str, meeting_purpose: str, tool_context: ToolContext) -> dict:
    """Save the client being prepared for, so the specialist research agents know who to research.
    Call this AFTER resolve_company and BEFORE transferring to meeting_prep_pipeline.

    Args:
        ticker: resolved ticker, e.g. "NWLG".
        company_name: resolved company name.
        meeting_purpose: what the banker said the meeting is about ("general catch-up" if not stated).
    """
    tool_context.state["client_ticker"] = ticker.upper()
    tool_context.state["client_name"] = company_name
    tool_context.state["meeting_purpose"] = meeting_purpose or "general coverage meeting"
    for key in ("internal_research_findings", "market_news_findings", "financial_findings"):
        tool_context.state[key] = ""
    return {"status": "ok", "client_ticker": ticker.upper(), "client_name": company_name}


def _client(ctx) -> str:
    s = ctx.state
    return (f"Client: {s.get('client_name', 'unknown')} (ticker {s.get('client_ticker', 'unknown')}). "
            f"Meeting purpose: {s.get('meeting_purpose', 'general coverage meeting')}. Today: {date.today():%d %b %Y}.")


# ---------------------------------------------------------------------------
# Specialist research agents (run in parallel)
# ---------------------------------------------------------------------------
internal_research_agent = LlmAgent(
    name="internal_research_agent",
    model=ADK_MODEL,
    description="Searches the bank's internal research library (RAG over PDFs).",
    instruction=lambda ctx: f"""You are the Internal Research specialist at an investment bank.
{_client(ctx)}

Use the `search_internal_research` tool (pass the ticker) at least 3 times with different queries to cover:
1. Our equity research view: rating, price target, thesis, estimates, key risks.
2. Relationship history: past deals, wallet share, key client contacts and their preferences.
3. Recent call reports, open opportunities (size, fee, probability, timing) and suggested talking points / sensitivities.

Then write concise bullet-point findings. After every bullet, cite the source in the form
[RAG: <document file name> p.<page>]. Only use facts returned by the tool. Do not invent data.""",
    tools=[search_internal_research],
    include_contents="none",
    output_key="internal_research_findings",
    generate_content_config=GEN_CONFIG,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

market_news_agent = LlmAgent(
    name="market_news_agent",
    model=ADK_MODEL,
    description="Finds the latest market news via the Web Search MCP.",
    instruction=lambda ctx: f"""You are the Market News specialist.
{_client(ctx)}

1. Call `search_news` with the company name (max_results 5).
2. Call `get_market_headlines` for today's macro / capital-markets backdrop.
Summarise the most meeting-relevant developments as bullets, newest first, each with its date and
cite as [Web: <publisher>, <published_date>]. Flag anything sensitive (activists, short reports, litigation).
Only use facts returned by the tools.""",
    tools=[_mcp_toolset("web_search_server.py")],
    include_contents="none",
    output_key="market_news_findings",
    generate_content_config=GEN_CONFIG,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

financial_data_agent = LlmAgent(
    name="financial_data_agent",
    model=ADK_MODEL,
    description="Pulls market data, fundamentals and consensus from the FactSet MCP.",
    instruction=lambda ctx: f"""You are the Financial Data specialist.
{_client(ctx)}

Call these FactSet tools for the ticker: `get_price_snapshot`, `get_fundamentals`,
`get_consensus_estimates`, `get_peer_comparison` and `get_ownership`.
Produce a compact summary with: a market-data table (price, 1D/YTD %, 52w range, market cap),
TTM financials and leverage, upcoming debt maturities if any, consensus vs. last quarter,
peer multiples and notable holders (especially activists). Use USD millions.
Cite every section as [FactSet]. Only use numbers returned by the tools.""",
    tools=[_mcp_toolset("factset_server.py")],
    include_contents="none",
    output_key="financial_findings",
    generate_content_config=GEN_CONFIG,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

research_team = ParallelAgent(
    name="research_team",
    description="Runs the internal research, market news and financial data agents concurrently.",
    sub_agents=[internal_research_agent, market_news_agent, financial_data_agent],
)

# ---------------------------------------------------------------------------
# Brief writer (synthesis)
# ---------------------------------------------------------------------------
brief_writer_agent = LlmAgent(
    name="brief_writer_agent",
    model=ADK_MODEL,
    description="Synthesises all research into a client meeting brief.",
    instruction=lambda ctx: f"""You are a senior investment banking associate writing a client meeting brief for a Managing Director.
{_client(ctx)}

Combine the three research inputs below into ONE well-structured Markdown brief. Keep the source
citations exactly as given ([RAG: ...], [Web: ...], [FactSet]) so the banker can see where each fact came from.

Structure:
# Meeting Brief: <Company> (<Ticker>)
**Meeting purpose** · **Prepared** <today>
## 1. Executive Summary  (3-5 bullets — the "if you read nothing else")
## 2. Company Snapshot & Market Data  (Markdown table)
## 3. Latest News & Market Context
## 4. Financial Highlights & Street View
## 5. Our Relationship & Internal View  (rating/PT, past deals, wallet share, key contacts table)
## 6. Opportunities to Pitch  (table: opportunity, size, est. fee, probability, timing)
## 7. Suggested Talking Points & Questions to Ask
## 8. Sensitivities / Topics to Avoid
## Sources  (group by: Internal Research RAG · Web Search MCP · FactSet MCP)

Be crisp and factual; do not invent information. If an input is empty, say that source was unavailable.

=== INTERNAL RESEARCH (RAG) ===
{ctx.state.get('internal_research_findings') or '(no data)'}

=== MARKET NEWS (Web Search MCP) ===
{ctx.state.get('market_news_findings') or '(no data)'}

=== FINANCIAL DATA (FactSet MCP) ===
{ctx.state.get('financial_findings') or '(no data)'}
""",
    include_contents="none",
    output_key="final_brief",
    generate_content_config=GEN_CONFIG,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

meeting_prep_pipeline = SequentialAgent(
    name="meeting_prep_pipeline",
    description="Prepares a full client meeting brief: parallel research across RAG, news and market data, then synthesis.",
    sub_agents=[research_team, brief_writer_agent],
)

# ---------------------------------------------------------------------------
# Root coordinator
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="client_brief_coordinator",
    model=ADK_MODEL,
    description="Investment banking client-brief assistant that orchestrates specialist agents.",
    instruction=lambda ctx: f"""You are "Client Brief", an AI assistant for investment bankers. Today is {date.today():%d %b %Y}.

When the banker asks you to prepare for a meeting / brief them on a client (by name or ticker):
1. Call `resolve_company` with the name or ticker they gave.
   - If it is not found, tell the banker and list the covered clients returned by the tool. Stop.
2. Call `set_meeting_context` with the resolved ticker, company name and the meeting purpose
   (infer it from the request, otherwise "general coverage meeting").
3. Transfer to the `meeting_prep_pipeline` agent, which spins up the specialist agents and writes the brief.
   Do not write the brief yourself.

For follow-up questions about a client that has already been briefed, answer from the conversation.
You may call `search_internal_research` for quick internal-document lookups; cite as [RAG: file p.page].
For greetings or unclear requests, briefly explain what you can do and give an example request,
e.g. "Prepare me for my meeting with Northwind Logistics" or "Brief me on HLXB".
Currently briefed client (if any): {ctx.state.get('client_name', 'none')}.""",
    tools=[
        _mcp_toolset("factset_server.py", tool_filter=["resolve_company"]),
        set_meeting_context,
        search_internal_research,
    ],
    sub_agents=[meeting_prep_pipeline],
    generate_content_config=GEN_CONFIG,
)
