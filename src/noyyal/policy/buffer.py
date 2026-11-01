from __future__ import annotations

import pandas as pd

from noyyal.config import FacilityTerms

DEFAULT_TARGET_INR = 50_000_000.0


def flat_buffer(forecast: pd.DataFrame, target_inr: float = DEFAULT_TARGET_INR) -> pd.DataFrame:
    """The shipped baseline: one flat target for all thirteen weeks."""
    return pd.DataFrame(
        {
            "week_start": pd.to_datetime(forecast["week_start"]),
            "min_cash_target_inr": float(target_inr),
        }
    )


def plan_buffer(forecast: pd.DataFrame, terms: FacilityTerms) -> pd.DataFrame:
    """Choose a minimum-cash target for each week.

    The decision is a U-curve: a high target costs carry (CC at 10.25% against
    a 6.4% liquid yield), while a low target risks the Friday wage check because
    liquid-fund redemptions settle T+1.

    ISSUE-04: implement.  A defensible approach is to grid-search targets on a
    rolling-origin backtest, keeping the simulated Friday-shortfall probability
    at or below 2%, then apply the chosen rule to the forecast.
    """
    raise NotImplementedError("ISSUE-04: implement plan_buffer()")
