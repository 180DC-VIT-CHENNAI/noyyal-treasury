from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from noyyal.config import FacilityTerms


@dataclass
class SimResult:
    total_cost_inr: float
    cc_interest_inr: float
    overdraw_interest_inr: float
    penalties_inr: float
    liquid_yield_inr: float
    min_cash_inr: float
    max_cc_inr: float
    shortfall_days: int
    covenant_breaches: int
    final_cash_inr: float
    final_cc_inr: float
    final_liquid_inr: float
    events: list[dict] = field(default_factory=list)


def _empty_result() -> SimResult:
    return SimResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def simulate(
    plan: pd.DataFrame,
    flows: pd.DataFrame,
    wages: pd.DataFrame,
    terms: FacilityTerms,
    opening: dict,
    calendar: pd.DataFrame | None = None,
) -> SimResult:
    """Replay a buffer plan against realised daily flows.

    The published rule (see docs/SCORING.md) is:

      * apply the day's flows;
      * if cash is above the week's target, sweep the excess into the liquid fund;
      * if cash would go negative, request a liquid-fund redemption and draw the
        CC line for the gap to zero (the target is a sweep threshold, not a
        borrowing target -- see docs/SCORING.md);
      * at 3 pm each Friday, if cash plus undrawn CC is below that week's wages,
        charge the shortfall penalty;
      * accrue CC interest daily and pay the liquid-fund yield.

    This shipped implementation contains two deliberate defects:

      * interest is accrued on actual/360 instead of actual/365 (ISSUE-05);
      * liquid-fund redemptions are credited the same day instead of T+1
        (ISSUE-05).

    The organisers' scorer uses the corrected version.  tests/test_simulator.py
    fails until both are fixed.
    """
    if flows.empty:
        return _empty_result()
    frame = flows.copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.normalize()
    frame["amount_inr"] = frame["amount_inr"].astype(float)
    plan_map = {
        pd.Timestamp(row.week_start).normalize(): float(row.min_cash_target_inr)
        for row in plan.itertuples()
    }
    wage_map = {}
    if not wages.empty:
        wage_frame = wages.copy()
        wage_frame["week_start"] = pd.to_datetime(wage_frame["week_start"]).dt.normalize()
        wage_map = dict(zip(wage_frame["week_start"], wage_frame["wages_inr"], strict=False))

    start = frame["date"].min()
    end = frame["date"].max()
    cash = float(opening["current_account_inr"])
    cc = float(opening["cc_drawn_inr"])
    liquid = float(opening.get("liquid_fund_inr", 0.0))
    pending: dict[pd.Timestamp, float] = {}
    cc_interest = 0.0
    overdraw_interest = 0.0
    penalties = 0.0
    liquid_yield = 0.0
    min_cash = cash
    max_cc = cc
    shortfall_days = 0
    covenant_breaches = 0
    over_streak = 0

    for day in pd.date_range(start, end, freq="D"):
        liquid_prev = liquid
        if day in pending:
            amount = pending.pop(day)
            liquid -= amount
            cash += amount

        today = frame[frame["date"] == day]
        wage_rows = today[today["category"] == "WAGES"]
        wages_due = float(wage_rows["amount_inr"].sum())
        non_wage = today[today["category"] != "WAGES"]
        cash += float(non_wage.loc[non_wage["direction"] == "IN", "amount_inr"].sum())
        cash -= float(non_wage.loc[non_wage["direction"] == "OUT", "amount_inr"].sum())

        week = day - pd.Timedelta(days=day.weekday())
        if day.weekday() == 4:
            wages_week = float(wage_map.get(week, wages_due))
            if cash + (terms.cc_limit_inr - cc) < wages_week:
                penalties += terms.shortfall_penalty_inr
                shortfall_days += 1

        cash -= wages_due
        target = plan_map.get(week, 0.0)
        if cash > target:
            liquid += cash - target
            cash = target
        elif cash < 0.0:
            gap = -cash
            redeem = min(gap, liquid)
            if redeem > 0:
                # Deliberate defect: T+0 credit.  The redemption should arrive
                # on the next business day, leaving a T+1 gap funded by CC.
                liquid -= redeem
                cash += redeem
            draw = gap - redeem
            cc += draw
            cash += draw

        if cc > terms.cc_limit_inr:
            over_streak += 1
            if over_streak == terms.overdraw_max_days + 1:
                penalties += terms.covenant_breach_penalty_inr
                covenant_breaches += 1
        else:
            over_streak = 0

        # Deliberate defect: actual/360 and T+0 yield on same-day sweeps.
        cc_interest += cc * terms.cc_rate / 360.0
        overdraw_interest += max(0.0, cc - terms.cc_limit_inr) * terms.overdraw_extra_rate / 360.0
        liquid_yield += liquid_prev * terms.liquid_yield / 360.0
        min_cash = min(min_cash, cash)
        max_cc = max(max_cc, cc)

    return SimResult(
        total_cost_inr=cc_interest + overdraw_interest + penalties - liquid_yield,
        cc_interest_inr=cc_interest,
        overdraw_interest_inr=overdraw_interest,
        penalties_inr=penalties,
        liquid_yield_inr=liquid_yield,
        min_cash_inr=min_cash,
        max_cc_inr=max_cc,
        shortfall_days=shortfall_days,
        covenant_breaches=covenant_breaches,
        final_cash_inr=cash,
        final_cc_inr=cc,
        final_liquid_inr=liquid,
    )
