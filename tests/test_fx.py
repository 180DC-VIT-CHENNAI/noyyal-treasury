"""ISSUE-01: these two tests fail until io/fx.py is fixed."""

import pandas as pd

from noyyal.io.fx import spot_rate, to_inr


def _row(bundle):
    return bundle.fx[bundle.fx["date"] == pd.Timestamp("2026-07-31")].iloc[0]


def test_usd_conversion_uses_spot(bundle):
    row = _row(bundle)
    amount = 10_000.0
    assert to_inr(amount, "USD", row) == amount * float(row["usdinr_spot"])


def test_eur_conversion_multiplies(bundle):
    row = _row(bundle)
    amount = 10_000.0
    assert to_inr(amount, "EUR", row) == amount * float(row["eurinr_spot"])
    assert spot_rate(row, "EUR") == float(row["eurinr_spot"])
