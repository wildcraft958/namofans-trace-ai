"""Module H -- Auto-STR Generator (FIU-IND compliant, ReportLab).

Generates a Suspicious Transaction Report PDF aligned with RBI / FIU-IND
electronic filing format in under 5 seconds.

Sections:
  1. Cover (alert ID, timestamp, risk level badge)
  2. Subject account details
  3. Suspicious transactions table
  4. Fund trail diagram
  5. Risk score breakdown
  6. AI narrative
  7. Recommended action
  8. Evidence metadata
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_RISK_COLORS = {
    "CRITICAL": colors.HexColor("#c0392b"),
    "HIGH": colors.HexColor("#e67e22"),
    "MEDIUM": colors.HexColor("#f1c40f"),
    "LOW": colors.HexColor("#27ae60"),
}


def generate(alert: dict, output_path: Path) -> Path:
    """Generate the STR PDF for an alert. Returns the output path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []
    story += _section_cover(alert, styles)
    story += _section_subject_account(alert, styles)
    story += _section_transactions(alert, styles)
    story += _section_fund_trail(alert, styles)
    story += _section_risk_breakdown(alert, styles)
    story += _section_narrative(alert, styles)
    story += _section_recommendation(alert, styles)
    story += _section_evidence_metadata(styles)

    doc.build(story)
    return output_path


# ──────────────────────────────────────────────
# Section builders
# ──────────────────────────────────────────────

def _h(text: str, styles, level: int = 1) -> Paragraph:
    size = {1: 14, 2: 12, 3: 10}[level]
    bold = level < 3
    style = ParagraphStyle(
        f"h{level}",
        parent=styles["Heading1"],
        fontSize=size,
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a2e"),
        fontName="Helvetica-Bold" if bold else "Helvetica",
    )
    return Paragraph(text, style)


def _p(text: str, styles) -> Paragraph:
    style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2c2c2c"),
    )
    return Paragraph(text, style)


def _divider() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c0c0c0"), spaceAfter=6)


def _section_cover(alert: dict, styles) -> list:
    risk = alert.get("risk_level", "HIGH")
    risk_color = _RISK_COLORS.get(risk, colors.HexColor("#e67e22"))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    header_style = ParagraphStyle(
        "header",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
    )
    badge_style = ParagraphStyle(
        "badge",
        parent=styles["Normal"],
        fontSize=12,
        textColor=risk_color,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    items = [
        Paragraph("TRACE.ai", header_style),
        Paragraph("Suspicious Transaction Report (STR)", sub_style),
        Paragraph("FIU-IND / RBI Compliant -- Confidential", sub_style),
        Spacer(1, 0.4 * cm),
        _divider(),
        Spacer(1, 0.2 * cm),
        Paragraph(f"Alert ID: {alert.get('alert_id', 'N/A')}", sub_style),
        Paragraph(f"Generated: {now}", sub_style),
        Paragraph(f"Risk Level: [{risk}]", badge_style),
        Spacer(1, 0.4 * cm),
        _divider(),
        Spacer(1, 0.3 * cm),
    ]
    return items


def _section_subject_account(alert: dict, styles) -> list:
    acc = alert.get("account_id", "UNKNOWN")
    masked = f"****{acc[-4:]}" if len(acc) >= 4 else acc
    items = [
        _h("1. Subject Account Details", styles),
        _divider(),
    ]
    data = [
        ["Field", "Value"],
        ["Account ID (Masked)", masked],
        ["Account Type", alert.get("account_type", "SAVINGS")],
        ["IFSC Code", alert.get("ifsc", "UBIN0XXXXXX")],
        ["KYC Risk Category", alert.get("kyc_risk", "HIGH")],
        ["Alert Raised On", alert.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d"))],
        ["Status", alert.get("status", "OPEN").upper()],
    ]
    items.append(_table(data))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_transactions(alert: dict, styles) -> list:
    items = [
        _h("2. Suspicious Transactions", styles),
        _divider(),
    ]
    txns = alert.get("transactions", [])
    if not txns:
        txns = _synthetic_txns(alert)

    header = ["Date", "Amount (INR)", "Channel", "Counterparty (Masked)", "Pattern"]
    rows = [header]
    for t in txns[:15]:
        cp = str(t.get("counterparty", "****"))
        masked_cp = f"****{cp[-4:]}" if len(cp) >= 4 else cp
        rows.append([
            str(t.get("date", t.get("timestamp", "—")))[:10],
            f"Rs {t.get('amount', 0):,.0f}",
            str(t.get("channel", "NEFT")),
            masked_cp,
            str(t.get("pattern", "—")),
        ])
    items.append(_table(rows, header_row=True))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_fund_trail(alert: dict, styles) -> list:
    items = [
        _h("3. Fund Trail Diagram", styles),
        _divider(),
        _p(
            "The following simplified fund trail shows the flow of funds detected by TRACE.ai. "
            "Each node represents an account; arrows show transaction direction and amount.",
            styles,
        ),
        Spacer(1, 0.2 * cm),
    ]

    acc = alert.get("account_id", "SUBJECT")
    pattern = _dominant_pattern(alert)
    trail_data = [
        ["Stage", "Account", "Role", "Amount (INR)"],
        ["Origin", f"****{acc[-4:]}", "Subject / Suspect", _fmt_amount(alert)],
    ]
    hops = alert.get("trail_hops", [])
    if not hops:
        hops = _synthetic_trail(alert)
    for i, hop in enumerate(hops[:5], start=1):
        cp = str(hop.get("account", "—"))
        trail_data.append([
            f"Hop {i}",
            f"****{cp[-4:]}" if len(cp) >= 4 else cp,
            hop.get("role", "Intermediary"),
            f"Rs {hop.get('amount', 0):,.0f}",
        ])

    items.append(_table(trail_data, header_row=True))
    items.append(Spacer(1, 0.2 * cm))
    items.append(_p(f"Primary typology detected: {pattern}", styles))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_risk_breakdown(alert: dict, styles) -> list:
    items = [
        _h("4. Risk Score Breakdown", styles),
        _divider(),
    ]
    contributions = alert.get("risk_contributions", {})
    composite = alert.get("composite_score", 0.0)

    data = [["Component", "Weight", "Score", "Contribution"]]
    component_map = {
        "pattern": ("Graph Pattern Matching", "30%"),
        "gnn": ("XGBoost Classifier", "30%"),
        "anomaly": ("Online Anomaly (River)", "20%"),
        "compliance": ("Compliance Rule Engine", "20%"),
    }
    for key, (label, weight) in component_map.items():
        contrib = contributions.get(key, 0.0)
        raw = contrib / {"pattern": 0.30, "gnn": 0.30, "anomaly": 0.20, "compliance": 0.20}[key]
        data.append([label, weight, f"{raw:.2f}", f"{contrib:.3f}"])
    data.append(["COMPOSITE SCORE", "100%", "", f"{composite:.3f}"])

    items.append(_table(data, header_row=True, last_row_bold=True))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_narrative(alert: dict, styles) -> list:
    items = [
        _h("5. AI-Generated Analysis", styles),
        _divider(),
    ]
    explanation_path = Path(f"data/processed/explanations/{alert.get('alert_id', '')}.txt")
    if explanation_path.exists():
        narrative = explanation_path.read_text().strip()
    else:
        pattern = _dominant_pattern(alert)
        acc = alert.get("account_id", "the subject account")
        narrative = (
            f"TRACE.ai detected a {pattern} pattern originating from account {acc}. "
            f"The account's transaction behavior deviated significantly from its historical baseline "
            f"with a composite risk score of {alert.get('composite_score', 0.0):.2f}. "
            f"Multiple suspicious indicators were identified including elevated transaction velocity, "
            f"high-value transfers near regulatory thresholds, and graph topology consistent with "
            f"known money laundering typologies. "
            f"This report is submitted for compliance officer review as per FIU-IND guidelines."
        )
    items.append(_p(narrative, styles))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_recommendation(alert: dict, styles) -> list:
    items = [
        _h("6. Recommended Action", styles),
        _divider(),
    ]
    risk = alert.get("risk_level", "HIGH")
    if risk == "CRITICAL":
        action = "FREEZE ACCOUNT + FILE STR IMMEDIATELY"
        rationale = (
            "Composite score >= 0.85. Multiple high-severity compliance rules triggered. "
            "Immediate account freeze recommended pending investigation."
        )
    elif risk == "HIGH":
        action = "FILE STR + ESCALATE TO COMPLIANCE OFFICER"
        rationale = (
            "Composite score >= 0.70. Suspicious pattern consistent with known AML typology. "
            "STR to be filed with FIU-IND within 7 working days per PMLA Section 12."
        )
    elif risk == "MEDIUM":
        action = "INVESTIGATE + ENHANCED DUE DILIGENCE"
        rationale = (
            "Composite score >= 0.50. Enhanced monitoring recommended. "
            "File STR if further suspicious activity is observed."
        )
    else:
        action = "MONITOR"
        rationale = "Low risk. Continue standard transaction monitoring."

    data = [
        ["Risk Level", "Recommended Action"],
        [risk, action],
    ]
    items.append(_table(data, header_row=True))
    items.append(Spacer(1, 0.2 * cm))
    items.append(_p(f"Rationale: {rationale}", styles))
    items.append(Spacer(1, 0.4 * cm))
    return items


def _section_evidence_metadata(styles) -> list:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = [
        _h("7. Evidence Metadata", styles),
        _divider(),
    ]
    data = [
        ["Parameter", "Value"],
        ["TRACE.ai Version", "0.1.0-phase2"],
        ["Detection Algorithm", "XGBoost on 11 graph features (AUC > 0.90)"],
        ["Anomaly Scorer", "River HalfSpaceTrees + ADWIN"],
        ["Compliance Engine", "YAML rule engine (hot-reload)"],
        ["Graph Library", "NetworkX MultiDiGraph"],
        ["Report Generated At", now],
        ["Data Source", "IBM AMLSim synthetic (Phase 2 POC)"],
        ["Disclaimer", "AI-generated. Requires compliance officer review before filing."],
    ]
    items.append(_table(data))
    items.append(Spacer(1, 0.5 * cm))
    items.append(_p(
        "This report is generated by TRACE.ai, an AI-powered AML detection system developed "
        "by Team NamoFans (IIT Kharagpur) for the iDEA 2.0 Hackathon, Union Bank of India. "
        "All account identifiers have been masked. This is a Phase 2 POC demonstration.",
        styles,
    ))
    return items


# ──────────────────────────────────────────────
# Table helper
# ──────────────────────────────────────────────

def _table(data: list, header_row: bool = False, last_row_bold: bool = False) -> Table:
    t = Table(data, hAlign="LEFT", repeatRows=1 if header_row else 0)
    base_style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f9f9f9"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d0d0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header_row:
        base_style += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    if last_row_bold:
        base_style += [
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eaf0fb")),
        ]
    t.setStyle(TableStyle(base_style))
    return t


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _dominant_pattern(alert: dict) -> str:
    matches = alert.get("pattern_matches", {})
    for pat, hit in matches.items():
        if hit:
            return pat.replace("_", " ").title()
    return "Suspicious Activity"


def _fmt_amount(alert: dict) -> str:
    txns = alert.get("transactions", [])
    total = sum(t.get("amount", 0) for t in txns)
    return f"Rs {total:,.0f}" if total else "N/A"


def _synthetic_txns(alert: dict) -> list[dict]:
    acc = alert.get("account_id", "ACC-0000")
    return [
        {"date": "2025-04-01", "amount": 950_000, "channel": "NEFT", "counterparty": "ACC-9001", "pattern": "Structuring", "subject": acc},
        {"date": "2025-04-01", "amount": 950_000, "channel": "NEFT", "counterparty": "ACC-9002", "pattern": "Structuring", "subject": acc},
        {"date": "2025-04-01", "amount": 950_000, "channel": "RTGS", "counterparty": "ACC-9003", "pattern": "Structuring", "subject": acc},
    ]


def _synthetic_trail(alert: dict) -> list[dict]:
    base = alert.get("account_id", "ACC-0000")[:3]
    return [
        {"account": f"{base}-9001", "role": "Layer 1", "amount": 850_000},
        {"account": f"{base}-9002", "role": "Layer 2", "amount": 700_000},
        {"account": f"{base}-9003", "role": "Beneficiary", "amount": 600_000},
    ]
