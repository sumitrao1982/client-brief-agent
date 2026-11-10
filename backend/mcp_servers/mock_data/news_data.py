"""Mock web/news search corpus (FICTITIOUS headlines and outlets).

Dates are expressed as "days ago" so the news always looks fresh when the demo runs.
"""

NEWS = [
    # --- Helix Biotherapeutics ---
    {"tickers": ["HLXB"], "days_ago": 1, "source": "BioPulse Wire (mock)",
     "title": "Helix Biotherapeutics confirms HELIOS-3 topline readout on track for Q1 2027",
     "snippet": "At an investor event, Helix CEO Dr. Elena Marsh reiterated that 52-week histology data for oral "
                "FGF21 analog HLX-201 is expected in Q1 2027 and that the trial's blinded safety review raised no new concerns.",
     "url": "https://news.example.com/helix-helios3-on-track"},
    {"tickers": ["HLXB"], "days_ago": 4, "source": "MarketLedger (mock)",
     "title": "Short seller report questions HLX-201 liver safety; Helix shares fall 6% intraday before recovering",
     "snippet": "A short-focused research firm published a report citing a Grade 3 ALT elevation in Phase 2b. Helix "
                "called the report 'misleading', noting the event resolved without discontinuation.",
     "url": "https://news.example.com/helix-short-report"},
    {"tickers": ["HLXB"], "days_ago": 9, "source": "Asia Pharma Today (mock)",
     "title": "Japanese drugmakers circle Western MASH assets as licensing frenzy grows",
     "snippet": "Two Japanese pharma companies are said to be in early discussions for Asian rights to late-stage MASH "
                "candidates, with Helix's HLX-201 frequently mentioned by people familiar with the matter.",
     "url": "https://news.example.com/japan-mash-licensing"},
    {"tickers": ["HLXB"], "days_ago": 15, "source": "BioPulse Wire (mock)",
     "title": "Helix Q3: Ventrexa royalties up 18%, cash runway into 2029",
     "snippet": "Helix reported Q3 revenue of $109M and a net loss of $0.63 per share, ahead of estimates. Cash and "
                "investments stood at $1.1B.",
     "url": "https://news.example.com/helix-q3-results"},

    # --- Northwind Logistics ---
    {"tickers": ["NWLG"], "days_ago": 1, "source": "FreightBeat (mock)",
     "title": "Northwind among bidders for cold-chain operator FrostLine, sources say",
     "snippet": "Northwind Logistics has signed an NDA and is preparing a first-round bid for FrostLine Holdings, which its "
                "private-equity owner values at about $2.1 billion including debt. First-round bids are due in late November.",
     "url": "https://news.example.com/northwind-frostline"},
    {"tickers": ["NWLG"], "days_ago": 3, "source": "MarketLedger (mock)",
     "title": "Activist Kestrel Capital sends letter urging Northwind to spin off intermodal unit",
     "snippet": "Kestrel, which owns 4.8% of Northwind, said a separation could unlock $20 per share of value and called "
                "for a $2B buyback. Northwind said it 'welcomes constructive dialogue with all shareholders'.",
     "url": "https://news.example.com/kestrel-northwind-letter"},
    {"tickers": ["NWLG"], "days_ago": 8, "source": "Credit Desk Daily (mock)",
     "title": "Rating agency revises Northwind outlook to positive on deleveraging",
     "snippet": "The agency cited leverage trending toward 2.5x and improving margins, but warned that a large debt-funded "
                "acquisition could reverse the trajectory.",
     "url": "https://news.example.com/northwind-outlook-positive"},
    {"tickers": ["NWLG"], "days_ago": 12, "source": "FreightBeat (mock)",
     "title": "Northwind beats Q3 estimates, lifts EBITDA guidance as freight cycle turns",
     "snippet": "Q3 revenue rose 6% to $3.04B; adjusted EBITDA margin expanded to 14.1%. FY2026 adjusted EBITDA guidance "
                "was raised to $1.60–1.65B.",
     "url": "https://news.example.com/northwind-q3"},

    # --- Aurora Renewable Power ---
    {"tickers": ["AURP"], "days_ago": 2, "source": "PowerGrid Journal (mock)",
     "title": "Aurora Renewable signs 600 MW PPA with hyperscale cloud provider for Texas data-center campus",
     "snippet": "The 15-year agreement covers a solar-plus-storage project expected online in 2028, bringing Aurora's "
                "year-to-date data-center contracted capacity to 1.1 GW.",
     "url": "https://news.example.com/aurora-hyperscaler-ppa"},
    {"tickers": ["AURP"], "days_ago": 6, "source": "Credit Desk Daily (mock)",
     "title": "Utilities' hybrid bond issuance hits record as power demand soars",
     "snippet": "Hybrid capital issuance by power companies reached a record this year; bankers expect renewable developers "
                "including Aurora to tap the market in early 2027.",
     "url": "https://news.example.com/utility-hybrids-record"},
    {"tickers": ["AURP"], "days_ago": 10, "source": "MarketLedger (mock)",
     "title": "Aurora explores sale of minority stake in 3 GW operating portfolio",
     "snippet": "Aurora is working on a potential sale of up to 49% of a portfolio of operating wind and solar assets, "
                "which could value the equity at about $2.5 billion.",
     "url": "https://news.example.com/aurora-stake-sale"},
    {"tickers": ["AURP"], "days_ago": 14, "source": "PowerGrid Journal (mock)",
     "title": "Solar panel tariff ruling raises capex for US developers by up to 8%",
     "snippet": "The ruling affects imported modules; analysts say large developers like Aurora have secured supply "
                "through 2027 but may face higher costs thereafter.",
     "url": "https://news.example.com/solar-tariff-ruling"},

    # --- Macro / market-wide ---
    {"tickers": ["MACRO"], "days_ago": 0, "source": "MarketLedger (mock)",
     "title": "Stocks edge higher as investors price in further rate cuts in 2027",
     "snippet": "The S&P 500 rose 0.4% while the 10-year Treasury yield slipped to 3.92%. IG credit spreads held near "
                "multi-year tights at about 98bps.",
     "url": "https://news.example.com/markets-close"},
    {"tickers": ["MACRO"], "days_ago": 2, "source": "Credit Desk Daily (mock)",
     "title": "Investment-grade issuance on pace for record November as issuers front-run 2027 maturity wall",
     "snippet": "Corporate borrowers are accelerating refinancing plans, with new-issue concessions averaging just 3bps.",
     "url": "https://news.example.com/ig-issuance-record"},
]
