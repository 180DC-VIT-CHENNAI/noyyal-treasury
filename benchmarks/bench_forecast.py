"""Small timing harness: baseline forecast over the public ledger."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from noyyal.forecast.seasonal_naive import SeasonalNaiveForecaster  # noqa: E402
from noyyal.io.loaders import load_bundle  # noqa: E402


def main() -> None:
    bundle = load_bundle(ROOT / "data" / "public")
    start = time.perf_counter()
    result = SeasonalNaiveForecaster().predict(
        bundle.ledger,
        pd.Timestamp("2026-07-31"),
        float(bundle.opening["current_account_inr"]),
    )
    elapsed = time.perf_counter() - start
    print(f"forecast rows={len(result)} elapsed={elapsed:.3f}s")
    print(result[["week_start", "net_p50_inr", "closing_p50_inr"]].to_string(index=False))


if __name__ == "__main__":
    main()
