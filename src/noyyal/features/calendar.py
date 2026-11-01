from __future__ import annotations

import pandas as pd


def week_start(values: pd.Series | list[pd.Timestamp]) -> pd.Series:
    """Monday starting each row's ISO week."""
    series = pd.to_datetime(pd.Series(values))
    return series - pd.to_timedelta(series.dt.weekday, unit="D")


def bank_holidays(calendar: pd.DataFrame) -> set[pd.Timestamp]:
    mask = calendar["is_bank_holiday_tn"].astype(bool)
    return set(pd.to_datetime(calendar.loc[mask, "date"]))


def days_to_festival(
    dates: pd.Series | list[pd.Timestamp],
    calendar: pd.DataFrame,
    name: str = "Diwali",
) -> pd.Series:
    """Days from each date to the next named festival.

    The bonus week moves every year, so week-of-year seasonality will miss it.
    calendar.csv already contains the 2026 dates.

    ISSUE-03: implement this without assuming a fixed ISO week.  The function
    must return a positive (or zero) number of calendar days for every input,
    including dates after the last festival record in the file.
    """
    raise NotImplementedError("ISSUE-03: implement days_to_festival() using calendar.csv")
