"""Generate sample *internal* bank documents (PDF) used to populate the RAG store.

All companies, people, numbers and events are FICTITIOUS and exist only to
demonstrate retrieval-augmented generation in the Client Brief agent.

Usage (from backend/):
    python scripts/generate_sample_pdfs.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "internal_docs"
BANK = "Meridian Capital Partners"  # fictional bank

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=colors.HexColor("#0B2545"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#13315C"))
BODY = ParagraphStyle("Body", parent=styles["BodyText"], leading=14, spaceAfter=6)
SMALL = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, textColor=colors.grey)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(
        0.75 * inch,
        0.5 * inch,
        f"{BANK} — INTERNAL / CONFIDENTIAL — SAMPLE DOCUMENT WITH FICTITIOUS DATA FOR DEMO PURPOSES",
    )
    canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _table(rows, col_widths=None):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#13315C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#8DA9C4")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF4ED")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


def build(filename: str, title: str, subtitle: str, sections: list):
    """sections: list of (heading, [paragraph strings | ('table', rows) | 'pagebreak'])"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER, title=title, author=BANK,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.75 * inch, bottomMargin=0.8 * inch,
    )
    story = [
        Paragraph(title, H1),
        Paragraph(subtitle, SMALL),
        Spacer(1, 10),
    ]
    for heading, items in sections:
        if heading:
            story.append(Paragraph(heading, H2))
        for item in items:
            if item == "pagebreak":
                story.append(PageBreak())
            elif isinstance(item, tuple) and item[0] == "table":
                story.append(_table(item[1]))
                story.append(Spacer(1, 8))
            else:
                story.append(Paragraph(item, BODY))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"  wrote {path.relative_to(OUT_DIR.parent.parent)}")


# ---------------------------------------------------------------------------
# HELIX BIOTHERAPEUTICS (HLXB)
# ---------------------------------------------------------------------------
def helix():
    build(
        "HLXB_Equity_Research_Note.pdf",
        "Helix Biotherapeutics Inc. (HLXB) — Initiation Update: Phase 3 Catalyst in Sight",
        f"{BANK} Equity Research | Healthcare – Biotechnology | Analyst: Priya Raman, PhD | Published: 14 Oct 2026",
        [
            ("Rating and Price Target", [
                "We reiterate our <b>OVERWEIGHT</b> rating on Helix Biotherapeutics (NASDAQ: HLXB) and raise our "
                "12-month price target to <b>$92</b> (from $85), implying ~29% upside to the last close of $71.40. "
                "Our risk-adjusted NPV now assigns a 62% probability of success (from 55%) to HLX-201 in MASH "
                "(metabolic dysfunction-associated steatohepatitis) following supportive Phase 2b open-label extension data.",
            ]),
            ("Investment Thesis", [
                "<b>1. HLX-201 is a potential best-in-class oral FGF21 analog.</b> The pivotal Phase 3 trial (HELIOS-3, "
                "n=1,180) completed enrollment in July 2026; topline 52-week histology readout is guided for Q1 2027. "
                "Our physician survey (n=45 hepatologists) suggests oral dosing would capture 35–40% share of new starts.",
                "<b>2. Ventrexa royalties provide a funding floor.</b> Partnered immunology product Ventrexa (marketed by a "
                "large-cap partner) generated $410M of royalty and milestone revenue over the trailing twelve months, "
                "growing 18% YoY, covering roughly 40% of operating expense.",
                "<b>3. Balance sheet is adequate but not excessive.</b> Cash and investments of $1.1B against a quarterly "
                "burn of ~$95M gives runway into 2029. However, a commercial launch of HLX-201 would require an incremental "
                "$600–800M, which we believe management will look to raise opportunistically on positive data.",
            ]),
            ("Financial Estimates (USD millions, except per share)", [
                ("table", [
                    ["Metric", "FY2025A", "FY2026E", "FY2027E", "FY2028E"],
                    ["Total revenue", "352", "425", "498", "910"],
                    ["R&D expense", "520", "565", "540", "480"],
                    ["SG&A expense", "140", "175", "260", "390"],
                    ["Operating income", "(308)", "(315)", "(302)", "40"],
                    ["EPS (diluted)", "(2.71)", "(2.62)", "(2.48)", "0.31"],
                    ["Year-end cash", "1,320", "1,040", "1,450*", "1,180"],
                ]),
                "<i>*FY2027E assumes a $750M equity or equity-linked raise following positive HELIOS-3 data.</i>",
            ]),
            ("Valuation", [
                "Our $92 target is derived from a sum-of-the-parts risk-adjusted NPV: HLX-201 MASH ($61/share), Ventrexa "
                "royalty stream ($19/share), early pipeline HLX-310 and HLX-415 ($6/share) and net cash ($6/share). We use "
                "a 10% WACC and 2% terminal decline post loss of exclusivity.",
            ]),
            ("Key Risks", [
                "(i) HELIOS-3 fails to meet its fibrosis-improvement endpoint; downside case $38/share. (ii) Competitive "
                "pressure from injectable GLP-1/FGF21 combinations. (iii) Dilution risk from a capital raise ahead of data. "
                "(iv) Hepatic safety signals – one Grade 3 ALT elevation was observed in Phase 2b.",
            ]),
            ("Analyst Takeaways for Coverage Bankers", [
                "Management has signalled at our September Healthcare Conference that they prefer a <b>convertible note</b> "
                "over straight equity to limit dilution, and are open to a <b>regional ex-US licensing deal</b> (Japan/China) "
                "for HLX-201 that could bring $150–250M upfront. These are both potential mandates for the firm.",
            ]),
        ],
    )

    build(
        "HLXB_Coverage_Relationship_Memo.pdf",
        "Client Coverage Memo — Helix Biotherapeutics Inc.",
        f"{BANK} Healthcare Investment Banking | Prepared by: Coverage Team (D. Okafor, MD) | Updated: 28 Oct 2026",
        [
            ("Relationship Overview", [
                "Helix has been a <b>Tier 1 coverage client</b> since 2021. The firm acted as joint bookrunner on Helix's "
                "$460M follow-on offering (March 2024) and as sole financial advisor on the Ventrexa royalty monetization "
                "discussions (2025, not executed). Estimated 3-year wallet paid to the firm: $14.2M; our wallet share is "
                "~22%, ranking #2 behind a bulge-bracket competitor.",
            ]),
            ("Key Client Contacts", [
                ("table", [
                    ["Name", "Title", "Relationship notes"],
                    ["Dr. Elena Marsh", "Chief Executive Officer", "Former Big Pharma R&D head; data-driven, dislikes long decks"],
                    ["Thomas Whitfield", "Chief Financial Officer", "Joined 2025 from a med-tech company; primary banking contact"],
                    ["Grace Lindqvist", "VP Corporate Development", "Leads licensing process; responsive on email"],
                    ["Arjun Mehta", "Board Member (Audit Chair)", "Ex-investment banker; sceptical of convertible pricing"],
                ]),
            ]),
            ("Recent Interactions (Call Reports)", [
                "<b>12 Sep 2026 – CFO lunch:</b> Whitfield asked for an update on the converts market for biotech issuers "
                "and indicative terms for a $500–750M 5-year convert with capped call. He noted the board wants to be "
                "'ready to go the day after data'.",
                "<b>03 Oct 2026 – Corp Dev call:</b> Lindqvist confirmed inbound interest from two Japanese pharma companies "
                "for HLX-201 Asian rights. She asked whether the firm could run a targeted process in Q4 2026.",
                "<b>21 Oct 2026 – CEO meeting at conference:</b> Dr. Marsh was frustrated by recent short-seller commentary "
                "on HLX-201 liver safety. Recommend we avoid discussing the short report unless she raises it.",
            ]),
            ("Open Opportunities", [
                ("table", [
                    ["Opportunity", "Est. size", "Est. fee", "Probability", "Timing"],
                    ["Convertible notes offering", "$600–750M", "$9–11M", "60%", "Q1–Q2 2027"],
                    ["HLX-201 Asia licensing advisory", "$150–250M upfront", "$4–6M", "40%", "Q4 2026–Q1 2027"],
                    ["Capped call / hedging", "n/a", "$1–2M", "50%", "With convert"],
                ]),
            ]),
            ("Suggested Talking Points for Next Meeting", [
                "1) Bring a one-page convert term sheet with pricing scenarios at current vol (pre- and post-data). "
                "2) Propose a 'shadow' licensing process starting December so a deal can be signed shortly after data. "
                "3) Reference our recent biotech convert execution experience. "
                "4) Sensitivity: CFO is cost-conscious on fees; the 2024 follow-on gross spread was negotiated down to 4.25%.",
            ]),
        ],
    )


# ---------------------------------------------------------------------------
# NORTHWIND LOGISTICS (NWLG)
# ---------------------------------------------------------------------------
def northwind():
    build(
        "NWLG_Equity_Research_Note.pdf",
        "Northwind Logistics Corp. (NWLG) — Q3 Review: Margin Recovery Intact, M&A Optionality Rising",
        f"{BANK} Equity Research | Industrials – Transportation & Logistics | Analyst: Marcus Feld, CFA | Published: 30 Oct 2026",
        [
            ("Rating and Price Target", [
                "We maintain our <b>EQUAL WEIGHT</b> rating on Northwind Logistics (NYSE: NWLG) with a price target of "
                "<b>$118</b> (from $112). Shares closed at $109.25. Q3 2026 revenue of $3.04B (+6% YoY) beat consensus by 2%, "
                "and adjusted EBITDA margin expanded 70bps to 14.1% on network optimisation and lower fuel costs.",
            ]),
            ("Q3 2026 Highlights", [
                "Freight brokerage volumes rebounded +9% YoY as the freight cycle turns. Contract logistics (warehousing) "
                "grew 11% driven by e-commerce customers. Intermodal remained soft (-3%). Management raised FY2026 adjusted "
                "EBITDA guidance to $1.60–1.65B (from $1.55–1.62B) and reiterated a medium-term target of 15% margin.",
            ]),
            ("Financial Estimates (USD millions, except per share)", [
                ("table", [
                    ["Metric", "FY2025A", "FY2026E", "FY2027E", "FY2028E"],
                    ["Revenue", "11,140", "11,820", "12,480", "13,150"],
                    ["Adj. EBITDA", "1,480", "1,625", "1,780", "1,920"],
                    ["Adj. EBITDA margin", "13.3%", "13.7%", "14.3%", "14.6%"],
                    ["Adj. EPS", "6.12", "6.85", "7.70", "8.45"],
                    ["Net debt", "5,250", "4,900", "4,450", "3,980"],
                    ["Net debt / EBITDA", "3.5x", "3.0x", "2.5x", "2.1x"],
                ]),
            ]),
            ("Capital Structure and Refinancing", [
                "Northwind has <b>$1.2B of 4.25% senior notes maturing in June 2027</b> and a $1.5B revolver expiring 2028. "
                "We expect the company to address the 2027 maturity in late 2026 or early 2027 via a new 7–10 year bond. At current "
                "BBB- spreads, a new issue would price around 5.6–5.9%, raising annual interest expense by ~$18M. The company is "
                "on positive outlook at one rating agency; reaching 2.5x leverage could trigger an upgrade to BBB.",
            ]),
            ("M&A and Activism", [
                "Activist fund <b>Kestrel Capital</b> disclosed a 4.8% stake in September 2026 and is pushing for a separation "
                "of the intermodal business and a larger buyback. Separately, press reports and our channel checks indicate "
                "Northwind is evaluating a bolt-on acquisition in <b>cold-chain logistics</b>; FrostLine Holdings (private, "
                "~$2.1B EV) is the most frequently cited target. A deal financed with ~50% debt would push leverage back to 3.4x.",
            ]),
            ("Valuation and Risks", [
                "Our $118 PT is based on 8.5x FY2027E EV/EBITDA, in line with the 5-year average and a modest discount to "
                "asset-light peers. Risks: freight recession relapse, customer concentration (top 10 customers = 31% of revenue), "
                "labour disputes at West Coast warehouses, and integration risk on any large acquisition.",
            ]),
        ],
    )

    build(
        "NWLG_Coverage_Relationship_Memo.pdf",
        "Client Coverage Memo — Northwind Logistics Corp.",
        f"{BANK} Industrials Investment Banking | Prepared by: Coverage Team (S. Alvarez, MD) | Updated: 4 Nov 2026",
        [
            ("Relationship Overview", [
                "Northwind is a <b>Tier 1 coverage client</b> and a lending relationship: the firm holds a $150M commitment "
                "in the $1.5B revolving credit facility. The firm was active bookrunner on the 2022 $800M bond and co-manager "
                "on the 2017 notes due 2027. 3-year wallet to the firm: $9.6M (wallet share ~15%, #4 among banks).",
            ]),
            ("Key Client Contacts", [
                ("table", [
                    ["Name", "Title", "Relationship notes"],
                    ["Robert Hale", "Chairman & CEO", "25-year company veteran; defensive about activist campaign"],
                    ["Linda Osei", "EVP & Chief Financial Officer", "Primary contact; focused on investment-grade rating"],
                    ["Kevin Brandt", "Treasurer", "Runs refinancing workstream; wants early read on bond demand"],
                    ["Sofia Romano", "SVP Strategy & M&A", "Owns cold-chain acquisition evaluation"],
                ]),
            ]),
            ("Recent Interactions (Call Reports)", [
                "<b>15 Sep 2026 – Treasurer call:</b> Brandt asked for a refinancing options analysis for the June 2027 notes, "
                "including a dual-tranche 7yr/10yr structure and a potential make-whole call on the existing notes.",
                "<b>08 Oct 2026 – Strategy session:</b> Romano shared that FrostLine's sponsor is running a sale process with "
                "first-round bids due late November. Northwind has signed an NDA. They have not yet appointed a sell-side "
                "or buy-side advisor — <b>this is our key opportunity</b>.",
                "<b>22 Oct 2026 – CFO dinner:</b> Osei is worried about Kestrel's demand to spin intermodal. She asked for a "
                "confidential defense preparedness review. CEO is sensitive on this topic; position it as 'shareholder engagement'.",
            ]),
            ("Open Opportunities", [
                ("table", [
                    ["Opportunity", "Est. size", "Est. fee", "Probability", "Timing"],
                    ["Buy-side advisory – FrostLine", "~$2.1B EV", "$12–15M", "45%", "Q4 2026–Q2 2027"],
                    ["Acquisition financing (bridge + bonds)", "$1.0–1.2B", "$6–8M", "40%", "With M&A"],
                    ["2027 notes refinancing", "$1.2B", "$3–4M", "70%", "Q1 2027"],
                    ["Activism defense advisory", "n/a", "$3–5M retainer", "35%", "Ongoing"],
                ]),
            ]),
            ("Suggested Talking Points for Next Meeting", [
                "1) Lead with a combined M&A + financing package for FrostLine showing pro-forma leverage and rating impact. "
                "2) Show that refinancing the 2027 notes early de-risks the balance sheet ahead of any acquisition. "
                "3) Offer a quiet shareholder-engagement review (do not use the word 'defense' with the CEO). "
                "4) Highlight the firm's cold-chain sector expertise and our existing revolver commitment.",
            ]),
        ],
    )


# ---------------------------------------------------------------------------
# AURORA RENEWABLE POWER (AURP)
# ---------------------------------------------------------------------------
def aurora():
    build(
        "AURP_Equity_Research_Note.pdf",
        "Aurora Renewable Power (AURP) — Data-Center Demand Re-rates the Growth Runway",
        f"{BANK} Equity Research | Utilities – Renewables | Analyst: Hannah Cole | Published: 22 Oct 2026",
        [
            ("Rating and Price Target", [
                "We reiterate <b>OVERWEIGHT</b> on Aurora Renewable Power (NYSE: AURP) and raise our price target to "
                "<b>$64</b> (from $60). Shares last closed at $55.80. Aurora signed 2.4 GW of new long-term PPAs year to date, "
                "of which 1.1 GW are with hyperscale data-center operators at prices ~12% above its legacy portfolio average.",
            ]),
            ("Investment Thesis", [
                "<b>1. Contracted growth:</b> Operating capacity of 11.6 GW with an 18 GW development pipeline (solar 55%, "
                "wind 25%, battery storage 20%). We model 1.8–2.0 GW of annual additions through 2030. "
                "<b>2. Tax-credit transferability:</b> Aurora monetised $640M of tax credits via transfer sales in 2026, "
                "reducing reliance on tax-equity partnerships. "
                "<b>3. Funding need is large but well-telegraphed:</b> 2027–2029 capex of ~$4.5B per year requires ~$1.5–2.0B "
                "of external capital annually; management prefers green bonds and hybrid capital to protect its BBB rating.",
            ]),
            ("Financial Estimates (USD millions, except per share)", [
                ("table", [
                    ["Metric", "FY2025A", "FY2026E", "FY2027E", "FY2028E"],
                    ["Revenue", "3,910", "4,320", "4,860", "5,410"],
                    ["Adj. EBITDA", "2,330", "2,610", "2,980", "3,350"],
                    ["CAFD per share", "2.18", "2.41", "2.66", "2.92"],
                    ["Dividend per share", "1.52", "1.62", "1.72", "1.83"],
                    ["Net debt / EBITDA", "5.4x", "5.2x", "5.1x", "4.9x"],
                ]),
            ]),
            ("Capital Markets Outlook", [
                "We expect Aurora to launch a <b>$1.5B inaugural green hybrid (junior subordinated) offering</b> in H1 2027, "
                "which receives 50% equity credit from rating agencies. An at-the-market (ATM) equity programme of $750M "
                "remains in place. A minority stake sale (up to 49%) in a 3 GW operating portfolio is also under consideration "
                "to recycle capital at an implied ~9x EV/EBITDA.",
            ]),
            ("Key Risks", [
                "Policy risk around federal tax-credit phase-downs; interconnection queue delays (avg. 3.5 years); panel "
                "tariffs raising solar capex 6–8%; rising rates compressing the valuation of long-duration contracted cash flows.",
            ]),
        ],
    )

    build(
        "AURP_Coverage_Relationship_Memo.pdf",
        "Client Coverage Memo — Aurora Renewable Power",
        f"{BANK} Power, Utilities & Infrastructure Banking | Prepared by: Coverage Team (J. Whitaker, MD) | Updated: 1 Nov 2026",
        [
            ("Relationship Overview", [
                "Aurora is a <b>Tier 1 strategic client</b>. The firm was green structuring agent and joint bookrunner on "
                "Aurora's $1.0B green bonds (2023 and 2025) and advised on the 2025 tax-credit transfer programme. "
                "3-year wallet to the firm: $18.3M (wallet share ~19%, #2).",
            ]),
            ("Key Client Contacts", [
                ("table", [
                    ["Name", "Title", "Relationship notes"],
                    ["Maya Thornton", "President & CEO", "Visionary; wants Aurora seen as 'the AI power company'"],
                    ["Daniel Reyes", "Chief Financial Officer", "Rating-focused; former rating-agency analyst"],
                    ["Chloe Nakamura", "Head of Capital Markets", "Day-to-day contact; runs bank league tables tightly"],
                    ["Oliver Grant", "Head of Sustainability", "Owns green financing framework and SPO process"],
                ]),
            ]),
            ("Recent Interactions (Call Reports)", [
                "<b>10 Sep 2026 – Capital markets update:</b> Nakamura requested a comparison of hybrid capital vs. "
                "preferred equity vs. minority asset sale for 2027 funding. She indicated three banks are pitching.",
                "<b>30 Sep 2026 – CFO meeting:</b> Reyes wants to keep FFO/debt above 13% (BBB threshold). He is concerned "
                "that a hybrid may be viewed as 'debt-like' by some investors.",
                "<b>20 Oct 2026 – CEO at energy conference:</b> Thornton is very interested in a joint venture with a hyperscaler "
                "to co-develop dedicated generation for data-center campuses — asked us for ideas on partner structures.",
            ]),
            ("Open Opportunities", [
                ("table", [
                    ["Opportunity", "Est. size", "Est. fee", "Probability", "Timing"],
                    ["Inaugural green hybrid", "$1.5B", "$7–9M", "55%", "H1 2027"],
                    ["Minority portfolio stake sale", "~$2.5B equity value", "$10–14M", "35%", "2027"],
                    ["Hyperscaler JV advisory", "n/a", "$5–8M", "25%", "2027"],
                    ["ATM programme agent", "$750M", "$1–2M", "60%", "Ongoing"],
                ]),
            ]),
            ("Suggested Talking Points for Next Meeting", [
                "1) Present a rating-agency-ready analysis of the hybrid with FFO/debt pro-forma impact. "
                "2) Show investor demand evidence from our recent utility hybrid placements. "
                "3) Bring 2–3 hyperscaler JV structure ideas for the CEO. "
                "4) Ensure green framework update (SPO) is coordinated with Oliver Grant early.",
            ]),
        ],
    )


# ---------------------------------------------------------------------------
# CROSS-SECTOR OUTLOOK
# ---------------------------------------------------------------------------
def sector_outlook():
    build(
        "Sector_Outlook_2027_Capital_Markets.pdf",
        "2027 Capital Markets & M&A Outlook — Coverage Sector Views",
        f"{BANK} Strategy & Research | Distribution: Investment Banking Coverage | Published: 5 Nov 2026",
        [
            ("Macro Backdrop", [
                "Our base case assumes the policy rate settles near 3.25% by mid-2027, IG credit spreads remain tight "
                "(+95–110bps), and equity volatility normalises. Equity capital markets issuance is expected to rise ~20% YoY "
                "led by healthcare and energy transition; IG bond issuance is forecast flat at elevated levels due to a large "
                "2027 maturity wall.",
            ]),
            ("Healthcare / Biotech", [
                "Biotech financing windows are open but highly catalyst-driven. Convertible notes have regained share "
                "(35% of biotech follow-on volume in 2026) as issuers seek to limit dilution. Licensing deals with Asian "
                "pharma partners have accelerated, with average upfronts of $180M for Phase 3 assets. MASH remains one of "
                "the most active therapeutic areas for partnering.",
            ]),
            ("Industrials / Logistics", [
                "Freight volumes are recovering after a two-year downturn. Strategic buyers are targeting cold-chain, "
                "temperature-controlled and pharma logistics assets, which trade at 11–13x EBITDA versus 7–9x for general "
                "freight. Activist campaigns in transport have doubled in 2026, typically targeting conglomerate discounts "
                "and capital returns.",
            ]),
            ("Power & Renewables", [
                "Data-center electricity demand is the dominant theme. Hyperscalers signed record PPA volumes in 2026 and "
                "increasingly seek equity partnerships in dedicated generation. Hybrid capital issuance by utilities reached "
                "a record $28B in 2026. Minority stake sales of operating renewables portfolios are clearing at 8.5–10x EBITDA.",
            ]),
            ("Implications for Coverage Bankers", [
                "Prioritise: (1) pre-positioning financing for catalyst-driven biotech clients, (2) combining M&A with "
                "acquisition financing for industrials clients, and (3) hybrid capital and capital recycling ideas for "
                "power clients. Always pair ideas with rating-agency impact analysis.",
            ]),
        ],
    )


if __name__ == "__main__":
    print("Generating sample internal PDFs (fictitious data)...")
    helix()
    northwind()
    aurora()
    sector_outlook()
    print("Done.")
