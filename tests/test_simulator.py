"""ISSUE-05: both tests fail while the simulator has its two deliberate defects."""

import pandas as pd

from noyyal.config import FacilityTerms
from noyyal.policy.simulator import simulate

TERMS = FacilityTerms(
    cc_limit_inr=60_000_000.0,
    cc_rate=0.1025,
    overdraw_extra_rate=0.02,
    overdraw_max_days=3,
    liquid_yield=0.064,
    liquid_settlement_days=1,
    shortfall_penalty_inr=5_000_000.0,
    covenant_breach_penalty_inr=2_500_000.0,
    actual_day_basis=365,
)


def _plan(week: pd.Timestamp, target: float) -> pd.DataFrame:
    return pd.DataFrame({"week_start": [week], "min_cash_target_inr": [target]})


def test_interest_uses_actual_365():
    day = pd.Timestamp("2026-08-03")
    flows = pd.DataFrame(
        {
            "date": [day, day],
            "category": ["EXPORT_RECEIPT", "DOMESTIC_RECEIPT"],
            "direction": ["IN", "IN"],
            "amount_inr": [0.0, 0.0],
        }
    )
    result = simulate(
        _plan(day, 0.0),
        flows,
        pd.DataFrame(columns=["week_start", "wages_inr"]),
        TERMS,
        {"current_account_inr": 0.0, "cc_drawn_inr": 10_000_000.0, "liquid_fund_inr": 0.0},
    )
    expected = 10_000_000.0 * 0.1025 / 365.0
    assert abs(result.cc_interest_inr - expected) < 1.0


def test_liquid_redemption_settles_t_plus_one():
    day = pd.Timestamp("2026-08-03")
    flows = pd.DataFrame(
        {
            "date": [day, day + pd.Timedelta(days=1)],
            "category": ["POWER", "OTHER"],
            "direction": ["OUT", "OUT"],
            "amount_inr": [1_000_000.0, 0.0],
        }
    )
    result = simulate(
        _plan(day, 5_000_000.0),
        flows,
        pd.DataFrame(columns=["week_start", "wages_inr"]),
        TERMS,
        {
            "current_account_inr": 0.0,
            "cc_drawn_inr": 0.0,
            "liquid_fund_inr": 10_000_000.0,
        },
    )
    # A T+1 redemption is still in the liquid fund on day 1.
    assert result.final_liquid_inr == 10_000_000.0
    assert result.final_cc_inr >= 1_000_000.0
