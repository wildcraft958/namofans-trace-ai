"""CSV / stream ingestion → internal Transaction schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_amlsim_csv(path: Path) -> pd.DataFrame:
    """Load AMLSim transaction CSV with standard columns."""
    raise NotImplementedError
