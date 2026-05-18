"""AMLSim output parser → TRACE.ai internal schema.

IBM AMLSim produces three CSV files in its output directory:
  - accounts.csv          : account metadata + IS_SAR flag
  - transactions.csv      : individual transactions + IS_SAR flag
  - alert_accounts.csv    : maps alert_id → account_id + alert_type

This module reads those CSVs and maps them to the Account / Transaction
dataclasses used throughout the TRACE.ai pipeline.

Column reference (AMLSim 2.x):
  accounts.csv     : ACCOUNT_ID, CUSTOMER_ID, INIT_BALANCE, START_DATE,
                     END_DATE, COUNTRY, ACCOUNT_TYPE, IS_SAR
  transactions.csv : TRAN_ID, ORIG_ACCT, BENE_ACCT, TX_TYPE,
                     TRAN_TIMESTAMP, BASE_AMT, IS_SAR
  alert_accounts.csv : ALERT_ID, ACCOUNT_ID, IS_SAR, ALERT_TYPE
"""

from __future__ import annotations

import random
import re
from datetime import datetime
from pathlib import Path
from trace.data.generator import Account, Transaction

import pandas as pd

# ── AMLSim TX_TYPE → Indian channel mapping ───────────────────────────────
_TX_TYPE_TO_CHANNEL: dict[str, str] = {
    "WIRE": "RTGS",
    "TRANSFER": "NEFT",
    "CASH": "ATM",
    "CREDIT": "IMPS",
    "DEBIT": "IMPS",
    "DEPOSIT": "UPI",
    "WITHDRAWAL": "ATM",
    "PAYMENT": "UPI",
    "OTHER": "NEFT",
}

# ── AMLSim ALERT_TYPE → TRACE fraud_type mapping ─────────────────────────
_ALERT_TYPE_TO_FRAUD_TYPE: dict[str, str] = {
    "cycle": "circular_flow",
    "circular": "circular_flow",
    "fan_in": "mule",
    "fan_out": "mule",
    "fan-in": "mule",
    "fan-out": "mule",
    "bipartite": "mule",
    "stack": "layering",
    "layering": "layering",
    "gather_scatter": "mule",
    "gather-scatter": "mule",
    "scatter_gather": "mule",
    "scatter-gather": "mule",
    "structuring": "structuring",
    "random": "dormant_burst",
    "mixed": "layering",
}

_IFSC_PREFIXES = ["UBIN", "SBIN", "HDFC", "ICIC", "PUNB", "BKID", "CNRB", "BARB"]
_ACCOUNT_TYPES = ["SAVINGS", "CURRENT", "SALARY", "LOAN"]
_KYC_RISKS = ["LOW", "MEDIUM", "HIGH"]
_FIRST_NAMES = [
    "Amit", "Priya", "Rahul", "Sunita", "Vikram", "Anita", "Rajesh", "Kavita",
    "Suresh", "Meena", "Arun", "Geeta", "Nitin", "Pooja", "Ravi", "Deepa",
]
_LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Joshi", "Yadav",
    "Mishra", "Tiwari", "Pandey", "Dubey", "Chauhan", "Rao", "Nair", "Mehta",
]


def _map_channel(tx_type: str) -> str:
    return _TX_TYPE_TO_CHANNEL.get(str(tx_type).upper(), "NEFT")


def _map_fraud_type(alert_type: str) -> str:
    key = str(alert_type).lower().strip()
    return _ALERT_TYPE_TO_FRAUD_TYPE.get(key, "layering")


def _map_account_type(aml_type: str) -> str:
    t = str(aml_type).upper()
    if t in ("CHECKING", "CURRENT"):
        return "CURRENT"
    if t in ("SAVINGS",):
        return "SAVINGS"
    if t in ("BUSINESS",):
        return "CURRENT"
    return "SAVINGS"


def _synthetic_ifsc(seed: int) -> str:
    rng = random.Random(seed)
    return f"{rng.choice(_IFSC_PREFIXES)}0{rng.randint(100000, 999999)}"


def _synthetic_name(seed: int) -> str:
    rng = random.Random(seed)
    return f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"


_BASE_DATE = datetime(2024, 1, 1)


def _parse_timestamp(val: object) -> datetime:
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    if isinstance(val, datetime):
        return val
    # AMLSim sample uses integer step numbers → offset from base date
    try:
        step = int(float(str(val)))
        if step >= 0:
            from datetime import timedelta
            return _BASE_DATE + timedelta(days=step)
    except (ValueError, OverflowError):
        pass
    s = str(val)
    # AMLSim uses formats like "2017-01-01" or "2017-01-01 00:00:00"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # fallback: strip timezone suffix and retry
    s_clean = re.sub(r"[+-]\d{2}:\d{2}$", "", s).strip()
    try:
        return datetime.fromisoformat(s_clean)
    except ValueError:
        return datetime(2025, 10, 1)


# ── Public loader ─────────────────────────────────────────────────────────

def load(output_dir: Path) -> tuple[list[Account], list[Transaction]] | None:
    """Load AMLSim CSVs from *output_dir*.

    Returns ``(accounts, transactions)`` on success, or ``None`` if the
    required files are not present.

    Expected files:
      {output_dir}/accounts.csv
      {output_dir}/transactions.csv
      {output_dir}/alert_accounts.csv  (optional but recommended)
    """
    output_dir = Path(output_dir)
    # AMLSim sample outputs use "nodes.csv"; full sim uses "accounts.csv"
    accts_path = output_dir / "accounts.csv"
    if not accts_path.exists():
        accts_path = output_dir / "nodes.csv"
    txns_path = output_dir / "transactions.csv"

    if not accts_path.exists() or not txns_path.exists():
        return None

    print(f"  [amlsim_loader] Reading accounts from {accts_path}")
    accts_df = pd.read_csv(accts_path, dtype=str)
    accts_df.columns = [c.strip().upper() for c in accts_df.columns]

    print(f"  [amlsim_loader] Reading transactions from {txns_path}")
    txns_df = pd.read_csv(txns_path, dtype=str)
    txns_df.columns = [c.strip().upper() for c in txns_df.columns]

    # ── Optional: alert_accounts for fraud_type labelling ─────────────────
    alert_accts_path = output_dir / "alert_accounts.csv"
    # account_id → fraud_type
    sar_fraud_type: dict[str, str] = {}
    if alert_accts_path.exists():
        print(f"  [amlsim_loader] Reading alert_accounts from {alert_accts_path}")
        alert_df = pd.read_csv(alert_accts_path, dtype=str)
        alert_df.columns = [c.strip().upper() for c in alert_df.columns]
        # Find alert type column (may be ALERT_TYPE or MODEL_ID or SCHEDULE_ID)
        type_col = next(
            (c for c in ("ALERT_TYPE", "MODEL_ID", "SCHEDULE_ID") if c in alert_df.columns),
            None,
        )
        acct_col = next(
            (c for c in ("ACCOUNT_ID", "ACCT_ID", "ACCOUNT") if c in alert_df.columns),
            None,
        )
        if acct_col:
            for _, row in alert_df.iterrows():
                aid = str(row[acct_col])
                atype = str(row[type_col]) if type_col else "stack"
                sar_fraud_type[aid] = _map_fraud_type(atype)

    # ── Build Account list ─────────────────────────────────────────────────
    # Detect column name variants
    def _col(df: pd.DataFrame, *candidates: str) -> str | None:
        for c in candidates:
            if c in df.columns:
                return c
        return None

    acc_id_col = _col(accts_df, "ACCOUNT_ID", "ACCT_ID", "NODEID", "ID")
    acc_type_col = _col(accts_df, "ACCOUNT_TYPE", "ACCT_TYPE", "TYPE")
    is_sar_col = _col(accts_df, "IS_SAR", "SAR", "FRAUD", "ISFRAUD")
    start_date_col = _col(accts_df, "START_DATE", "OPEN_DATE", "DATE")

    if acc_id_col is None:
        raise ValueError(
            f"Cannot find account ID column in {accts_path}. "
            f"Columns present: {list(accts_df.columns)}"
        )

    accounts: list[Account] = []
    for i, row in accts_df.iterrows():
        aid = str(row[acc_id_col])
        is_sar = str(row[is_sar_col]).strip() in ("1", "true", "True", "TRUE", "yes") if is_sar_col else False

        # Derive age_days from START_DATE if available
        age_days = 365
        if start_date_col and str(row[start_date_col]).strip() not in ("", "nan"):
            try:
                start = _parse_timestamp(row[start_date_col])
                age_days = max(1, (datetime(2025, 10, 1) - start).days)
            except Exception:
                pass

        # High-risk accounts are sar-flagged; mark dormant if they look inactive
        kyc_risk = "HIGH" if is_sar else "MEDIUM" if i % 7 == 0 else "LOW"
        dormant_days = 60 if is_sar else 0

        accounts.append(Account(
            account_id=aid,
            account_type=_map_account_type(str(row[acc_type_col]) if acc_type_col else "SAVINGS"),
            ifsc=_synthetic_ifsc(hash(aid) & 0xFFFFFF),
            kyc_risk=kyc_risk,
            age_days=age_days,
            dormant_days=dormant_days,
            name=_synthetic_name(hash(aid) & 0xFFFFFF),
        ))

    # ── Build Transaction list ─────────────────────────────────────────────
    txn_id_col = _col(txns_df, "TRAN_ID", "TXN_ID", "TRANSACTION_ID", "ID")
    orig_col = _col(txns_df, "ORIG_ACCT", "SENDER", "FROM_ACCT", "ORIG_ACCOUNT", "ORIG", "SOURCENODEID")
    bene_col = _col(txns_df, "BENE_ACCT", "RECEIVER", "TO_ACCT", "BENE_ACCOUNT", "BENE", "TARGETNODEID")
    type_col_t = _col(txns_df, "TX_TYPE", "TXN_TYPE", "TYPE", "CHANNEL")
    ts_col = _col(txns_df, "TRAN_TIMESTAMP", "TIMESTAMP", "DATE", "TRAN_DATE", "TX_DATE", "TIME")
    amt_col = _col(txns_df, "BASE_AMT", "AMOUNT", "AMT", "BASE_AMOUNT", "VALUE")
    is_sar_t_col = _col(txns_df, "IS_SAR", "SAR", "FRAUD", "ISFRAUD")

    if orig_col is None or bene_col is None:
        raise ValueError(
            f"Cannot find sender/receiver columns in {txns_path}. "
            f"Columns present: {list(txns_df.columns)}"
        )

    transactions: list[Transaction] = []
    for i, row in txns_df.iterrows():
        orig = str(row[orig_col])
        bene = str(row[bene_col])
        is_sar = str(row[is_sar_t_col]).strip() in ("1", "true", "True", "TRUE", "yes") if is_sar_t_col else False

        # Determine fraud type from alert_accounts lookup, else from is_sar flag
        if is_sar:
            fraud_type = sar_fraud_type.get(orig) or sar_fraud_type.get(bene) or "layering"
        else:
            fraud_type = ""

        ts = _parse_timestamp(row[ts_col]) if ts_col else datetime(2025, 10, 1)
        amount = float(str(row[amt_col]).replace(",", "")) if amt_col else 10000.0
        channel = _map_channel(str(row[type_col_t])) if type_col_t else "NEFT"

        txn_id = str(row[txn_id_col]) if txn_id_col else f"TXN-{i:07d}"

        transactions.append(Transaction(
            txn_id=txn_id,
            sender=orig,
            receiver=bene,
            amount=round(amount, 2),
            timestamp=ts,
            channel=channel,
            fraud_label=is_sar,
            fraud_type=fraud_type,
        ))

    sar_acct_count = sum(1 for a in accounts if a.kyc_risk == "HIGH")
    sar_txn_count = sum(1 for t in transactions if t.fraud_label)
    print(
        f"  [amlsim_loader] Loaded {len(accounts)} accounts "
        f"({sar_acct_count} SAR-flagged), "
        f"{len(transactions)} transactions "
        f"({sar_txn_count} SAR-flagged)"
    )
    return accounts, transactions
