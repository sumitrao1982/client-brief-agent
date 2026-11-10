"""Mock Web Search / News MCP server (stdio).

Simulates a web-search MCP (e.g. a Brave/Tavily/Google search MCP) returning the
latest market news. All articles are FICTITIOUS and served from mock_data/news_data.py.

Run standalone for debugging:  python mcp_servers/web_search_server.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from mock_data.factset_data import COMPANIES, resolve  # noqa: E402
from mock_data.news_data import NEWS  # noqa: E402

mcp = MCPServer(
    name="web-search-mock",
    instructions="Mock web search MCP server returning recent news articles.",
)

SOURCE = "Web Search MCP (mock)"


def _format(article: dict) -> dict:
    published = date.today() - timedelta(days=article["days_ago"])
    return {
        "title": article["title"],
        "snippet": article["snippet"],
        "publisher": article["source"],
        "published_date": published.isoformat(),
        "url": article["url"],
    }


@mcp.tool()
def search_news(query: str, max_results: int = 5, days: int = 30) -> dict:
    """Search the web for the latest news articles about a company, ticker or topic.

    Args:
        query: free-text query, e.g. "Northwind Logistics" or "NWLG acquisition".
        max_results: maximum number of articles to return (default 5).
        days: only return articles published within this many days (default 30).
    """
    ticker = resolve(query)
    words = [w for w in query.lower().split() if len(w) > 3]
    hits = []
    for a in NEWS:
        if a["days_ago"] > days:
            continue
        text = (a["title"] + " " + a["snippet"]).lower()
        if (ticker and ticker in a["tickers"]) or any(w in text for w in words):
            hits.append(a)
    hits.sort(key=lambda a: a["days_ago"])
    return {
        "query": query,
        "resolved_ticker": ticker,
        "company": COMPANIES[ticker]["name"] if ticker else None,
        "results": [_format(a) for a in hits[:max_results]],
        "source": SOURCE,
    }


@mcp.tool()
def get_market_headlines(max_results: int = 3) -> dict:
    """Return today's top macro / capital-markets headlines (rates, credit, equity markets)."""
    macro = sorted([a for a in NEWS if "MACRO" in a["tickers"]], key=lambda a: a["days_ago"])
    return {"results": [_format(a) for a in macro[:max_results]], "source": SOURCE}


if __name__ == "__main__":
    mcp.run(transport="stdio")
