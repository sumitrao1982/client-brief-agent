"""Mock FactSet-style market & fundamentals data (FICTITIOUS companies and numbers)."""

COMPANIES = {
    "HLXB": {
        "entity_id": "FS-0HLX-E",
        "name": "Helix Biotherapeutics Inc.",
        "aliases": ["helix", "helix bio", "helix biotherapeutics"],
        "exchange": "NASDAQ",
        "sector": "Health Care",
        "industry": "Biotechnology",
        "hq": "Boston, MA, USA",
        "employees": 1180,
        "description": "Clinical/commercial-stage biotech developing oral FGF21 analog HLX-201 for MASH; "
                       "receives royalties on partnered immunology drug Ventrexa.",
        "price": {"last": 71.40, "change_pct_1d": 1.85, "change_pct_ytd": 24.3, "high_52w": 78.10,
                  "low_52w": 49.25, "market_cap_mm": 8420, "avg_volume_3m": 1_640_000, "beta": 1.32,
                  "short_interest_pct": 9.8},
        "fundamentals": {
            "currency": "USD", "units": "millions",
            "ttm": {"revenue": 410, "ebitda": -268, "net_income": -291, "eps": -2.66,
                    "cash_and_investments": 1100, "total_debt": 0, "net_debt": -1100, "quarterly_burn": 95},
            "history": [
                {"fiscal_year": 2023, "revenue": 241, "ebitda": -335, "net_income": -352, "eps": -3.41},
                {"fiscal_year": 2024, "revenue": 298, "ebitda": -301, "net_income": -318, "eps": -2.92},
                {"fiscal_year": 2025, "revenue": 352, "ebitda": -289, "net_income": -296, "eps": -2.71},
            ],
            "last_reported_quarter": {"period": "Q3 2026", "revenue": 109, "eps": -0.63, "vs_consensus_eps": "+0.05 beat"},
        },
        "estimates": {"fy2026e": {"revenue": 431, "eps": -2.58}, "fy2027e": {"revenue": 505, "eps": -2.41},
                      "num_analysts": 19, "ratings": {"buy": 13, "hold": 5, "sell": 1},
                      "mean_price_target": 88.50, "high_price_target": 120.0, "low_price_target": 45.0},
        "peers": [
            {"ticker": "PEER-B1*", "name": "Late-stage MASH Peer A (mock)", "ev_to_sales": 14.2, "market_cap_mm": 9100},
            {"ticker": "PEER-B2*", "name": "MASH Peer B (mock)", "ev_to_sales": None, "market_cap_mm": 4300},
            {"ticker": "PEER-B3*", "name": "Metabolic Peer C (mock)", "ev_to_sales": None, "market_cap_mm": 6200},
        ],
        "ownership": [
            {"holder": "Granite Peak Asset Mgmt (mock)", "pct": 11.2},
            {"holder": "Blue Harbor Life Sciences Fund (mock)", "pct": 8.4},
            {"holder": "Index Fund Complex A (mock)", "pct": 7.1},
        ],
        "credit": {"rating": "Not rated", "outlook": None},
    },
    "NWLG": {
        "entity_id": "FS-0NWL-E",
        "name": "Northwind Logistics Corp.",
        "aliases": ["northwind", "northwind logistics"],
        "exchange": "NYSE",
        "sector": "Industrials",
        "industry": "Freight & Logistics",
        "hq": "Chicago, IL, USA",
        "employees": 41500,
        "description": "Asset-light freight brokerage, contract logistics/warehousing and intermodal provider "
                       "across North America.",
        "price": {"last": 109.25, "change_pct_1d": -0.62, "change_pct_ytd": 15.8, "high_52w": 114.60,
                  "low_52w": 86.40, "market_cap_mm": 14210, "avg_volume_3m": 2_120_000, "beta": 1.08,
                  "short_interest_pct": 2.1},
        "fundamentals": {
            "currency": "USD", "units": "millions",
            "ttm": {"revenue": 11690, "ebitda": 1598, "net_income": 612, "eps": 6.71,
                    "cash_and_investments": 420, "total_debt": 5410, "net_debt": 4990, "net_debt_to_ebitda": 3.1},
            "history": [
                {"fiscal_year": 2023, "revenue": 11920, "ebitda": 1560, "net_income": 590, "eps": 6.35},
                {"fiscal_year": 2024, "revenue": 10880, "ebitda": 1390, "net_income": 498, "eps": 5.44},
                {"fiscal_year": 2025, "revenue": 11140, "ebitda": 1480, "net_income": 560, "eps": 6.12},
            ],
            "last_reported_quarter": {"period": "Q3 2026", "revenue": 3040, "eps": 1.86, "vs_consensus_eps": "+0.09 beat"},
            "debt_maturities": [
                {"instrument": "4.25% Senior Notes", "amount_mm": 1200, "maturity": "2027-06-15"},
                {"instrument": "Revolving Credit Facility ($1.5B, $300M drawn)", "amount_mm": 300, "maturity": "2028-03-31"},
                {"instrument": "5.10% Senior Notes", "amount_mm": 800, "maturity": "2032-09-01"},
            ],
        },
        "estimates": {"fy2026e": {"revenue": 11790, "eps": 6.80, "ebitda": 1618},
                      "fy2027e": {"revenue": 12410, "eps": 7.62, "ebitda": 1765},
                      "num_analysts": 22, "ratings": {"buy": 9, "hold": 12, "sell": 1},
                      "mean_price_target": 116.40, "high_price_target": 135.0, "low_price_target": 92.0},
        "peers": [
            {"ticker": "PEER-L1*", "name": "Large-cap Freight Broker (mock)", "ev_to_ebitda": 11.4, "pe_ntm": 24.1},
            {"ticker": "PEER-L2*", "name": "Contract Logistics Peer (mock)", "ev_to_ebitda": 9.8, "pe_ntm": 19.5},
            {"ticker": "PEER-L3*", "name": "Intermodal Carrier (mock)", "ev_to_ebitda": 8.1, "pe_ntm": 16.2},
        ],
        "ownership": [
            {"holder": "Index Fund Complex A (mock)", "pct": 9.6},
            {"holder": "Kestrel Capital (activist, mock)", "pct": 4.8},
            {"holder": "Lakeshore Value Partners (mock)", "pct": 4.1},
        ],
        "credit": {"rating": "BBB- / Baa3", "outlook": "Positive (one agency)"},
    },
    "AURP": {
        "entity_id": "FS-0AUR-E",
        "name": "Aurora Renewable Power",
        "aliases": ["aurora", "aurora renewable", "aurora renewables", "aurora power"],
        "exchange": "NYSE",
        "sector": "Utilities",
        "industry": "Renewable Electricity",
        "hq": "Denver, CO, USA",
        "employees": 3900,
        "description": "Independent renewable power producer with 11.6 GW operating solar, wind and storage "
                       "capacity and an 18 GW development pipeline.",
        "price": {"last": 55.80, "change_pct_1d": 0.94, "change_pct_ytd": 18.7, "high_52w": 58.35,
                  "low_52w": 41.10, "market_cap_mm": 22640, "avg_volume_3m": 3_480_000, "beta": 0.86,
                  "short_interest_pct": 3.4},
        "fundamentals": {
            "currency": "USD", "units": "millions",
            "ttm": {"revenue": 4210, "ebitda": 2540, "net_income": 690, "eps": 1.70,
                    "cash_and_investments": 910, "total_debt": 14460, "net_debt": 13550, "net_debt_to_ebitda": 5.3,
                    "ffo_to_debt_pct": 13.6},
            "history": [
                {"fiscal_year": 2023, "revenue": 3280, "ebitda": 1940, "net_income": 512, "eps": 1.31},
                {"fiscal_year": 2024, "revenue": 3560, "ebitda": 2110, "net_income": 575, "eps": 1.45},
                {"fiscal_year": 2025, "revenue": 3910, "ebitda": 2330, "net_income": 630, "eps": 1.57},
            ],
            "last_reported_quarter": {"period": "Q3 2026", "revenue": 1180, "eps": 0.52, "vs_consensus_eps": "+0.03 beat"},
        },
        "estimates": {"fy2026e": {"revenue": 4300, "eps": 1.74, "ebitda": 2600},
                      "fy2027e": {"revenue": 4820, "eps": 1.95, "ebitda": 2960},
                      "num_analysts": 17, "ratings": {"buy": 12, "hold": 5, "sell": 0},
                      "mean_price_target": 62.10, "high_price_target": 70.0, "low_price_target": 50.0},
        "peers": [
            {"ticker": "PEER-R1*", "name": "Large Renewable Developer (mock)", "ev_to_ebitda": 12.8, "dividend_yield": 3.1},
            {"ticker": "PEER-R2*", "name": "Contracted Yieldco (mock)", "ev_to_ebitda": 10.9, "dividend_yield": 5.6},
            {"ticker": "PEER-R3*", "name": "Integrated Utility w/ Renewables (mock)", "ev_to_ebitda": 11.5, "dividend_yield": 3.8},
        ],
        "ownership": [
            {"holder": "Index Fund Complex A (mock)", "pct": 10.3},
            {"holder": "Global Infrastructure Pension (mock)", "pct": 6.9},
            {"holder": "Green Transition Fund (mock)", "pct": 5.2},
        ],
        "credit": {"rating": "BBB / Baa2", "outlook": "Stable"},
    },
}


def resolve(query: str):
    """Resolve a company name or ticker to a ticker in the mock universe."""
    q = (query or "").strip().lower().replace("$", "")
    if not q:
        return None
    for ticker, c in COMPANIES.items():
        if q == ticker.lower() or q == c["name"].lower() or q in c["aliases"]:
            return ticker
    for ticker, c in COMPANIES.items():  # fuzzy contains match
        if q in c["name"].lower() or any(a in q for a in c["aliases"]) or ticker.lower() in q.split():
            return ticker
    return None
