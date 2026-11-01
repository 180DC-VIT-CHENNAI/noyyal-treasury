from __future__ import annotations

from typing import Any


def spot_rate(fx_row: Any, currency: str) -> float:
    """Return the spot INR rate for a currency on a row of fx_daily.csv."""
    if currency == "USD":
        return float(fx_row["usdinr_spot"])
    if currency == "EUR":
        return float(fx_row["eurinr_spot"])
    if currency == "INR":
        return 1.0
    raise ValueError(f"Unsupported currency: {currency}")


def forward_rate(fx_row: Any, currency: str, tenor: str = "3m") -> float:
    if currency == "USD" and tenor == "3m":
        return float(fx_row["usdinr_fwd_3m"])
    if currency == "USD" and tenor == "1m":
        return float(fx_row["usdinr_fwd_1m"])
    if currency == "EUR" and tenor == "3m":
        return float(fx_row["eurinr_fwd_3m"])
    raise ValueError(f"No forward rate for {currency}/{tenor}")


def to_inr(amount_fcy: float, currency: str, fx_row: Any) -> float:
    """Convert a foreign amount to rupees.

    This helper is used by the invoice-level forecast.  It is also the subject
    of ISSUE-01: the current implementation is wrong in two ways.

    * It prices settled transactions off the 3-month forward instead of spot.
    * It divides on the EUR path instead of multiplying.

    tests/test_fx.py encodes both expectations.  Fix the function, not the test.
    """
    if currency == "USD":
        return float(amount_fcy) * forward_rate(fx_row, "USD", "3m")
    if currency == "EUR":
        return float(amount_fcy) / forward_rate(fx_row, "EUR", "3m")
    if currency == "INR":
        return float(amount_fcy)
    raise ValueError(f"Unsupported currency: {currency}")
