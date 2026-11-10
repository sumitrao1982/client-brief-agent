"""Mock FactSet MCP server (stdio).

Exposes FactSet-style tools for market data, fundamentals, estimates, peers and
ownership. All data is FICTITIOUS and served from mock_data/factset_data.py.

Run standalone for debugging:  python mcp_servers/factset_server.py
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from mock_data.factset_data import COMPANIES, resolve  # noqa: E402

mcp = MCPServer(
    name="factset-mock",
    instructions="Mock FactSet MCP server providing market data, fundamentals and consensus estimates.",
)

SOURCE = "FactSet MCP (mock)"


def _company(ticker_or_name: str):
    ticker = resolve(ticker_or_name)
    if not ticker:
        return None, {
            "error": f"No FactSet entity found for '{ticker_or_name}'.",
            "covered_universe": [f"{t} - {c['name']}" for t, c in COMPANIES.items()],
            "source": SOURCE,
        }
    return ticker, None


def _meta():
    return {"source": SOURCE, "as_of": date.today().isoformat()}


@mcp.tool()
def resolve_company(query: str) -> dict:
    """Resolve a company name or ticker to its FactSet entity (ticker, name, exchange, sector).

    Args:
        query: company name, partial name or ticker, e.g. "Northwind" or "NWLG".
    """
    ticker, err = _company(query)
    if err:
        return err
    c = COMPANIES[ticker]
    return {
        "ticker": ticker, "entity_id": c["entity_id"], "name": c["name"], "exchange": c["exchange"],
        "sector": c["sector"], "industry": c["industry"], "hq": c["hq"], "employees": c["employees"],
        "description": c["description"], **_meta(),
    }


@mcp.tool()
def get_price_snapshot(ticker: str) -> dict:
    """Latest price, daily/YTD performance, 52-week range, market cap and short interest for a ticker."""
    ticker, err = _company(ticker)
    if err:
        return err
    return {"ticker": ticker, "currency": "USD", **COMPANIES[ticker]["price"], **_meta()}


@mcp.tool()
def get_fundamentals(ticker: str) -> dict:
    """Trailing-twelve-month and historical financials (revenue, EBITDA, net income, EPS, debt, cash)."""
    ticker, err = _company(ticker)
    if err:
        return err
    c = COMPANIES[ticker]
    return {"ticker": ticker, **c["fundamentals"], "credit_rating": c["credit"], **_meta()}


@mcp.tool()
def get_consensus_estimates(ticker: str) -> dict:
    """Street consensus estimates, analyst rating distribution and price targets."""
    ticker, err = _company(ticker)
    if err:
        return err
    return {"ticker": ticker, **COMPANIES[ticker]["estimates"], **_meta()}


@mcp.tool()
def get_peer_comparison(ticker: str) -> dict:
    """Trading comparables for the company's closest peers."""
    ticker, err = _company(ticker)
    if err:
        return err
    return {"ticker": ticker, "peers": COMPANIES[ticker]["peers"], **_meta()}


@mcp.tool()
def get_ownership(ticker: str) -> dict:
    """Top institutional shareholders (including any activist positions)."""
    ticker, err = _company(ticker)
    if err:
        return err
    return {"ticker": ticker, "top_holders": COMPANIES[ticker]["ownership"], **_meta()}


if __name__ == "__main__":
    mcp.run(transport="stdio")
