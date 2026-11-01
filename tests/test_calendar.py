"""ISSUE-03: days_to_festival() is a stub and this test fails initially."""

import pandas as pd

from noyyal.features.calendar import days_to_festival, week_start


def test_week_start_is_monday():
    out = week_start(pd.Series([pd.Timestamp("2026-10-30")]))
    assert out.iloc[0] == pd.Timestamp("2026-10-26")


def test_diwali_2026_bonus_week(bundle):
    dates = pd.Series([pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-08")])
    days = days_to_festival(dates, bundle.calendar, "Diwali")
    assert list(days) == [9, 0]
