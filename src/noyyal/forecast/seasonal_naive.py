from __future__ import annotations

import pandas as pd

from noyyal.forecast.base import forecast_weeks, weekly_aggregate


class SeasonalNaiveForecaster:
    """The shipped baseline: same ISO week last year, scaled by YoY growth.

    It deliberately ignores the open invoice book, the bonus calendar, and the
    purchase commitments.  It is the floor the reference solution must beat.
    """

    def __init__(
        self,
        growth_window_weeks: int = 13,
        inflow_band: tuple[float, float] = (0.65, 1.35),
        outflow_band: tuple[float, float] = (0.82, 1.18),
    ) -> None:
        self.growth_window_weeks = growth_window_weeks
        self.inflow_band = inflow_band
        self.outflow_band = outflow_band

    def _growth(self, weekly: pd.DataFrame, as_of: pd.Timestamp, column: str) -> float:
        recent_start = pd.Timestamp(as_of) - pd.Timedelta(weeks=self.growth_window_weeks)
        last_year_start = recent_start - pd.Timedelta(weeks=52)
        recent = weekly[(weekly["week_start"] > recent_start) & (weekly["week_start"] <= as_of)]
        last_year = weekly[
            (weekly["week_start"] > last_year_start) & (weekly["week_start"] <= last_year_start + pd.Timedelta(days=91))
        ]
        recent_sum = float(recent[column].sum())
        last_sum = float(last_year[column].sum())
        if last_sum <= 0:
            return 1.0
        return float(min(1.30, max(0.80, recent_sum / last_sum)))

    def predict(
        self,
        ledger: pd.DataFrame,
        as_of: pd.Timestamp,
        opening_cash_inr: float,
        horizon_weeks: int = 13,
    ) -> pd.DataFrame:
        weekly = weekly_aggregate(ledger).set_index("week_start")
        growth_in = self._growth(weekly.reset_index(), as_of, "inflow_inr")
        growth_out = self._growth(weekly.reset_index(), as_of, "outflow_inr")
        rows = []
        for week in forecast_weeks(as_of, horizon_weeks):
            prior = week - pd.Timedelta(weeks=52)
            if prior in weekly.index:
                base_in = float(weekly.loc[prior, "inflow_inr"])
                base_out = float(weekly.loc[prior, "outflow_inr"])
            else:
                window = weekly.loc[
                    (weekly.index >= prior - pd.Timedelta(weeks=2))
                    & (weekly.index <= prior + pd.Timedelta(weeks=2))
                ]
                base_in = float(window["inflow_inr"].mean()) if len(window) else 0.0
                base_out = float(window["outflow_inr"].mean()) if len(window) else 0.0
            inflow = max(0.0, base_in * growth_in)
            outflow = max(0.0, base_out * growth_out)
            low_in = inflow * self.inflow_band[0]
            high_in = inflow * self.inflow_band[1]
            low_out = outflow * self.outflow_band[0]
            high_out = outflow * self.outflow_band[1]
            rows.append(
                {
                    "week_start": week,
                    "inflow_p50_inr": inflow,
                    "outflow_p50_inr": outflow,
                    "net_p10_inr": low_in - high_out,
                    "net_p50_inr": inflow - outflow,
                    "net_p90_inr": high_in - low_out,
                }
            )
        frame = pd.DataFrame(rows)
        frame["closing_p10_inr"] = float(opening_cash_inr) + frame["net_p10_inr"].cumsum()
        frame["closing_p50_inr"] = float(opening_cash_inr) + frame["net_p50_inr"].cumsum()
        frame["closing_p90_inr"] = float(opening_cash_inr) + frame["net_p90_inr"].cumsum()
        return frame
