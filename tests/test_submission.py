import json

import pandas as pd

from noyyal.forecast.seasonal_naive import SeasonalNaiveForecaster
from noyyal.hedge.forward import baseline_hedge_book
from noyyal.policy.buffer import flat_buffer
from noyyal.submission import validate_buffer, validate_forecast, validate_hedge, write_submission


def _payload(book, ratio=1.0):
    return {
        "hedge_ratio": {"USD": ratio, "EUR": ratio},
        "tenor_policy": "SINGLE",
        "forwards": [
            {
                "currency": row.currency,
                "notional_fcy": float(row.notional_fcy),
                "maturity_date": str(pd.Timestamp(row.maturity_date).date()),
            }
            for row in book.itertuples()
        ],
    }


def test_submission_round_trip(bundle, tmp_path):
    as_of = pd.Timestamp("2026-07-31")
    forecast = SeasonalNaiveForecaster().predict(
        bundle.ledger, as_of, float(bundle.opening["current_account_inr"])
    )
    plan = flat_buffer(forecast)
    book = baseline_hedge_book(bundle.receivables, bundle.fx, as_of)
    payload = _payload(book)
    validate_forecast(forecast)
    validate_buffer(plan, bundle.terms)
    validate_hedge(payload, bundle.receivables)
    manifest = write_submission(tmp_path, forecast, plan, payload, bundle.terms, bundle.receivables)
    assert (tmp_path / "forecast.csv").exists()
    assert (tmp_path / "buffer_plan.csv").exists()
    assert (tmp_path / "hedge.json").exists()
    assert (tmp_path / "manifest.json").exists()
    written = json.loads((tmp_path / "manifest.json").read_text())
    assert written["files"]
    assert manifest["case_id"] == "c1-noyyal"
