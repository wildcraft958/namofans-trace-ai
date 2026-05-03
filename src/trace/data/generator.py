"""Synthetic Indian banking transaction generator.

Wraps IBM AMLSim output and augments it with Indian banking fields
(IFSC codes, INR amounts, KYC risk categories, dormancy status).

TODO(ml): wire AMLSim CLI invocation; today this only emits a stub schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    txn_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: datetime
    channel: str  # NEFT | RTGS | UPI | IMPS | BRANCH | ATM | MOBILE
    fraud_label: bool = False


@dataclass
class Account:
    account_id: str
    account_type: str  # SAVINGS | CURRENT | SALARY | LOAN
    ifsc: str
    kyc_risk: str  # LOW | MEDIUM | HIGH
    age_days: int
    dormant_days: int


def generate(num_accounts: int = 5_000, num_transactions: int = 100_000) -> tuple[list[Account], list[Transaction]]:
    """Generate synthetic accounts and transactions. Returns (accounts, transactions)."""
    raise NotImplementedError("Wire AMLSim + Faker(en_IN) here.")
