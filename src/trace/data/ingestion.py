"""CSV / stream ingestion → internal Transaction schema."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from trace.data.generator import Account, Transaction

import pandas as pd

_TXN_COLS = ["txn_id", "sender", "receiver", "amount", "timestamp", "channel", "fraud_label", "fraud_type"]
_ACC_COLS = ["account_id", "account_type", "ifsc", "kyc_risk", "age_days", "dormant_days", "name"]


def load_amlsim_csv(path: Path) -> pd.DataFrame:
    """Load AMLSim / generated transaction CSV. Returns DataFrame with canonical columns."""
    df = pd.read_csv(path, parse_dates=["timestamp"])
    for col in ["fraud_label", "fraud_type"]:
        if col not in df.columns:
            df[col] = False if col == "fraud_label" else ""
    df["fraud_label"] = df["fraud_label"].astype(bool)
    return df.reindex(columns=_TXN_COLS)  # type: ignore[return-value]


def load_accounts_csv(path: Path) -> pd.DataFrame:
    """Load accounts CSV. Returns DataFrame with canonical columns."""
    df = pd.read_csv(path)
    if "name" not in df.columns:
        df["name"] = ""
    return df.reindex(columns=_ACC_COLS)  # type: ignore[return-value]


def df_to_accounts(df: pd.DataFrame) -> list[Account]:
    return [
        Account(
            account_id=str(row["account_id"]),
            account_type=str(row["account_type"]),
            ifsc=str(row["ifsc"]),
            kyc_risk=str(row["kyc_risk"]),
            age_days=int(row["age_days"]),
            dormant_days=int(row["dormant_days"]),
            name=str(row.get("name", "")),
        )
        for _, row in df.iterrows()
    ]


def df_to_transactions(df: pd.DataFrame) -> list[Transaction]:
    txns = []
    for _, row in df.iterrows():
        ts = row["timestamp"]
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime()  # type: ignore[assignment]
        elif not isinstance(ts, datetime):
            ts = datetime.fromisoformat(str(ts))
        txns.append(Transaction(
            txn_id=str(row["txn_id"]),
            sender=str(row["sender"]),
            receiver=str(row["receiver"]),
            amount=float(row["amount"]),
            timestamp=ts,  # type: ignore[arg-type]
            channel=str(row["channel"]),
            fraud_label=bool(row["fraud_label"]),
            fraud_type=str(row.get("fraud_type", "")),
        ))
    return txns
