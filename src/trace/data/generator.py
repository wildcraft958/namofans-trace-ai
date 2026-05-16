"""Synthetic Indian banking transaction generator.

Generates 5,000 accounts + 100,000 transactions with 5 seeded fraud rings:
  1. Circular flow ring (5 accounts, ₹5L per hop)
  2. Layering chain (6 accounts, ₹18L → ₹6L forwarding)
  3. Structuring cluster (3 accounts, 4x ₹9.5L same-day)
  4. Mule fan-in/fan-out (12 → aggregator → 8 receivers)
  5. Dormant burst (95 days inactive → 5x ₹8L in 6 hours)
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np


@dataclass
class Transaction:
    txn_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: datetime
    channel: str  # NEFT | RTGS | UPI | IMPS | ATM
    fraud_label: bool = False
    fraud_type: str = ""


@dataclass
class Account:
    account_id: str
    account_type: str  # SAVINGS | CURRENT | SALARY | LOAN
    ifsc: str
    kyc_risk: str  # LOW | MEDIUM | HIGH
    age_days: int
    dormant_days: int
    name: str = ""


_CHANNELS = ["UPI", "NEFT", "IMPS", "RTGS", "ATM"]
_CHANNEL_WEIGHTS = [0.40, 0.25, 0.20, 0.10, 0.05]
_ACCOUNT_TYPES = ["SAVINGS", "CURRENT", "SALARY", "LOAN"]
_ACCOUNT_TYPE_WEIGHTS = [0.55, 0.25, 0.15, 0.05]
_KYC_RISKS = ["LOW", "MEDIUM", "HIGH"]
_KYC_WEIGHTS = [0.65, 0.25, 0.10]
_IFSC_PREFIXES = ["UBIN", "SBIN", "HDFC", "ICIC", "PUNB", "BKID", "CNRB", "BARB"]
_FIRST_NAMES = [
    "Amit", "Priya", "Rahul", "Sunita", "Vikram", "Anita", "Rajesh", "Kavita",
    "Suresh", "Meena", "Arun", "Geeta", "Nitin", "Pooja", "Ravi", "Deepa",
    "Manoj", "Neha", "Sanjay", "Ritu", "Ashok", "Shweta", "Dinesh", "Usha",
]
_LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Joshi", "Yadav",
    "Mishra", "Tiwari", "Pandey", "Dubey", "Chauhan", "Rao", "Nair", "Mehta",
]


def _ifsc(rng: random.Random) -> str:
    return f"{rng.choice(_IFSC_PREFIXES)}0{rng.randint(100000, 999999)}"


def _name(rng: random.Random) -> str:
    return f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"


def _channel(rng: random.Random) -> str:
    return rng.choices(_CHANNELS, weights=_CHANNEL_WEIGHTS, k=1)[0]


def _ts(rng: random.Random, base: datetime, window_days: int = 90) -> datetime:
    return base + timedelta(seconds=rng.randint(0, window_days * 86400))


def generate(
    num_accounts: int = 5_000,
    num_transactions: int = 100_000,
    seed: int = 42,
    output_dir: Path | None = None,
) -> tuple[list[Account], list[Transaction]]:
    """Generate synthetic accounts + transactions. Returns (accounts, transactions)."""
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    base = datetime(2025, 10, 1)

    # ── Clean accounts ────────────────────────────────────────────────────────
    accounts: list[Account] = [
        Account(
            account_id=f"ACC-{i:05d}",
            account_type=rng.choices(_ACCOUNT_TYPES, weights=_ACCOUNT_TYPE_WEIGHTS, k=1)[0],
            ifsc=_ifsc(rng),
            kyc_risk=rng.choices(_KYC_RISKS, weights=_KYC_WEIGHTS, k=1)[0],
            age_days=rng.randint(30, 3650),
            dormant_days=rng.randint(0, 30),
            name=_name(rng),
        )
        for i in range(num_accounts)
    ]
    ids = [a.account_id for a in accounts]

    # ── Clean transactions (log-normal INR amounts) ───────────────────────────
    amounts = np.clip(np_rng.lognormal(mean=10.5, sigma=1.8, size=num_transactions), 100, 10_000_000)
    transactions: list[Transaction] = []
    ctr = 0

    for i in range(num_transactions):
        s = rng.choice(ids)
        r = rng.choice(ids)
        while r == s:
            r = rng.choice(ids)
        transactions.append(Transaction(
            txn_id=f"TXN-{ctr:07d}",
            sender=s,
            receiver=r,
            amount=round(float(amounts[i]), 2),
            timestamp=_ts(rng, base),
            channel=_channel(rng),
        ))
        ctr += 1

    def add_account(acc_id: str, kyc: str = "HIGH", dormant: int = 5) -> None:
        accounts.append(Account(
            account_id=acc_id,
            account_type=rng.choice(["SAVINGS", "CURRENT"]),
            ifsc=_ifsc(rng),
            kyc_risk=kyc,
            age_days=rng.randint(90, 730),
            dormant_days=dormant,
            name=_name(rng),
        ))

    def add_txn(sender: str, receiver: str, amount: float, ts: datetime,
                channel: str, fraud_type: str) -> None:
        nonlocal ctr
        transactions.append(Transaction(
            txn_id=f"TXN-{ctr:07d}",
            sender=sender, receiver=receiver,
            amount=amount, timestamp=ts, channel=channel,
            fraud_label=True, fraud_type=fraud_type,
        ))
        ctr += 1

    # ── Fraud ring 1: Circular flow ───────────────────────────────────────────
    cf = [f"RING-CF-{j:02d}" for j in range(5)]
    for a in cf:
        add_account(a)
    t0 = base + timedelta(days=45)
    for j in range(5):
        for _ in range(3):
            add_txn(cf[j], cf[(j + 1) % 5], 500_000.0,
                    t0 + timedelta(hours=rng.randint(0, 48)), "NEFT", "circular_flow")

    # ── Fraud ring 2: Layering chain ─────────────────────────────────────────
    ly = [f"RING-LY-{j:02d}" for j in range(6)]
    for a in ly:
        add_account(a)
    t0 = base + timedelta(days=20)
    layer_amounts = [1_800_000, 1_300_000, 950_000, 680_000, 490_000]
    for j in range(5):
        add_txn(ly[j], ly[j + 1], float(layer_amounts[j]),
                t0 + timedelta(hours=j * 8), "RTGS", "layering")

    # ── Fraud ring 3: Structuring ─────────────────────────────────────────────
    st_sender = "RING-ST-00"
    st_recv = [f"RING-ST-{j:02d}" for j in range(1, 4)]
    add_account(st_sender, kyc="MEDIUM", dormant=10)
    for a in st_recv:
        add_account(a, kyc="LOW", dormant=rng.randint(0, 15))
    t0 = base + timedelta(days=60)
    for j in range(4):
        add_txn(st_sender, st_recv[j % 3], 950_000.0,
                t0 + timedelta(hours=j * 2, minutes=rng.randint(5, 55)), "UPI", "structuring")

    # ── Fraud ring 4: Mule fan-in / fan-out ──────────────────────────────────
    mu_agg = "RING-MU-00"
    mu_in = [f"RING-MU-{j:02d}" for j in range(1, 13)]
    mu_out = [f"RING-MU-{j:02d}" for j in range(13, 21)]
    for a in [mu_agg, *mu_in, *mu_out]:
        add_account(a)
    t0 = base + timedelta(days=35)
    for s in mu_in:
        add_txn(s, mu_agg, float(rng.randint(80_000, 200_000)),
                t0 + timedelta(hours=rng.randint(0, 6)), _channel(rng), "mule")
    for r in mu_out:
        add_txn(mu_agg, r, float(rng.randint(100_000, 300_000)),
                t0 + timedelta(hours=rng.randint(8, 18)), _channel(rng), "mule")

    # ── Fraud ring 5: Dormant burst ───────────────────────────────────────────
    db_src = "RING-DB-00"
    db_recv = [f"RING-DB-{j:02d}" for j in range(1, 6)]
    accounts.append(Account(
        account_id=db_src, account_type="SAVINGS", ifsc=_ifsc(rng),
        kyc_risk="MEDIUM", age_days=1200, dormant_days=95, name=_name(rng),
    ))
    for a in db_recv:
        add_account(a, kyc="LOW", dormant=0)
    t0 = base + timedelta(days=88)
    for j, r in enumerate(db_recv):
        add_txn(db_src, r, 800_000.0,
                t0 + timedelta(hours=j + 1, minutes=rng.randint(0, 45)), "IMPS", "dormant_burst")

    # ── Write CSV if requested ────────────────────────────────────────────────
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "transactions.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["txn_id", "sender", "receiver", "amount", "timestamp",
                        "channel", "fraud_label", "fraud_type"])
            for t in transactions:
                w.writerow([t.txn_id, t.sender, t.receiver, t.amount,
                            t.timestamp.isoformat(), t.channel, int(t.fraud_label), t.fraud_type])
        with open(output_dir / "accounts.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["account_id", "account_type", "ifsc", "kyc_risk",
                        "age_days", "dormant_days", "name"])
            for a in accounts:
                w.writerow([a.account_id, a.account_type, a.ifsc, a.kyc_risk,
                            a.age_days, a.dormant_days, a.name])

    return accounts, transactions
