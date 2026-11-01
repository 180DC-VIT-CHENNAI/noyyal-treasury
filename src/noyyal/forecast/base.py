from __future__ import annotations

from typing import Protocol

import numpy as np
import pandas as pd

EXCLUDED_CATEGORIES = {"INTEREST_CC", "FUND_SWEEP"}


class Forecaster(Protocol):
    def predict(
        self,
        ledger: pd.DataFrame,
        as_of: pd.Timestamp,
        opening_cash_inr: float,
        horizon_weeks: int = 13,
    ) -> pd.DataFrame: ...


def weekly_aggregate(ledger: pd.DataFrame) -> pd.DataFrame:
    """Aggregate operating cash flow by Monday-starting week."""
    frame = ledger.copy()
    frame = frame[~frame["category"].isin(EXCLUDED_CATEGORIES)]
    dates = pd.to_datetime(frame["value_date"])
    frame["week_start"] = dates - pd.to_timedelta(dates.dt.weekday, unit="D")
    frame["inflow_inr"] = np.where(frame["direction"] == "IN", frame["amount_inr"], 0.0)
    frame["outflow_inr"] = np.where(frame["direction"] == "OUT", frame["amount_inr"], 0.0)
    out = (
        frame.groupby("week_start", as_index=False)[["inflow_inr", "outflow_inr"]]
        .sum()
        .sort_values("week_start")
        .reset_index(drop=True)
    )
    out["net_inr"] = out["inflow_inr"] - out["outflow_inr"]
    return out


def first_forecast_week(as_of: pd.Timestamp) -> pd.Timestamp:
    """Monday of the first full week strictly after as_of."""
    stamp = pd.Timestamp(as_of).normalize()
    candidate = stamp + pd.Timedelta(days=(7 - stamp.weekday()) % 7)
    if candidate <= stamp:
        candidate += pd.Timedelta(days=7)
    return candidate


def forecast_weeks(as_of: pd.Timestamp, horizon_weeks: int = 13) -> pd.DatetimeIndex:
    start = first_forecast_week(as_of)
    return pd.date_range(start, periods=horizon_weeks, freq="7D")


def wape(actual: pd.Series, predicted: pd.Series) -> float:
    actual = pd.Series(actual, dtype=float)
    predicted = pd.Series(predicted, dtype=float)
    denominator = float(actual.abs().sum())
    if denominator == 0:
        return float("inf")
    return float((actual - predicted).abs().sum() / denominator)


def pinball_loss(actual: float, predicted: float, quantile: float) -> float:
    error = float(actual) - float(predicted)
    return max(quantile * error, (quantile - 1.0) * error)


def mean_pinball_loss(
    actual: pd.Series, p10: pd.Series, p50: pd.Series, p90: pd.Series
) -> float:
    losses = []
    for a, q10, q50, q90 in zip(actual, p10, p50, p90, strict=True):
        losses.append(pinball_loss(a, q10, 0.1))
        losses.append(pinball_loss(a, q50, 0.5))
        losses.append(pinball_loss(a, q90, 0.9))
    return float(np.mean(losses))


def interval_coverage(actual: pd.Series, p10: pd.Series, p90: pd.Series) -> float:
    actual = pd.Series(actual, dtype=float)
    covered = (actual >= pd.Series(p10, dtype=float)) & (actual <= pd.Series(p90, dtype=float))
    return float(covered.mean())


def rolling_origin_backtest(
    ledger: pd.DataFrame,
    origins: list[pd.Timestamp],
    predictor,
    horizon_weeks: int = 13,
) -> pd.DataFrame:
    """Run a predictor at several origins and return per-week errors.

    `predictor(history, origin)` must return a frame with week_start and
    inflow_p50_inr / outflow_p50_inr.  The helper is given so teams can compare
    their model with the seasonal naive baseline on a common footing.
    """
    rows = []
    for origin in origins:
        history = ledger[pd.to_datetime(ledger["value_date"]) <= origin]
        pred = predictor(history, origin).set_index("week_start")
        actual = weekly_aggregate(ledger).set_index("week_start")
        for week in forecast_weeks(origin, horizon_weeks):
            if week not in actual.index or week not in pred.index:
                continue
            rows.append(
                {
                    "origin": origin,
                    "week_start": week,
                    "actual_inflow": float(actual.loc[week, "inflow_inr"]),
                    "pred_inflow": float(pred.loc[week, "inflow_p50_inr"]),
                    "actual_outflow": float(actual.loc[week, "outflow_inr"]),
                    "pred_outflow": float(pred.loc[week, "outflow_p50_inr"]),
                }
            )
    return pd.DataFrame(rows)
