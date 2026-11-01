import pandas as pd

from noyyal.forecast.base import first_forecast_week, forecast_weeks
from noyyal.forecast.seasonal_naive import SeasonalNaiveForecaster


def test_forecast_window_starts_next_monday(bundle):
    as_of = pd.Timestamp("2026-07-31")
    assert first_forecast_week(as_of) == pd.Timestamp("2026-08-03")
    weeks = forecast_weeks(as_of)
    assert len(weeks) == 13
    assert weeks[-1] == pd.Timestamp("2026-10-26")


def test_baseline_shape_and_ordering(bundle):
    as_of = pd.Timestamp("2026-07-31")
    result = SeasonalNaiveForecaster().predict(
        bundle.ledger, as_of, float(bundle.opening["current_account_inr"])
    )
    assert len(result) == 13
    assert (result["net_p10_inr"] <= result["net_p50_inr"]).all()
    assert (result["net_p50_inr"] <= result["net_p90_inr"]).all()
    assert (result["closing_p10_inr"] <= result["closing_p90_inr"]).all()
