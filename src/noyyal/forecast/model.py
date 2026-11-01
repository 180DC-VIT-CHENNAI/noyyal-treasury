from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from noyyal.io.loaders import DataBundle


@dataclass
class CashForecaster:
    """The team's forecaster.

    A strong solution builds weekly inflows from the open invoice book and
    weekly outflows from payroll, the open PO book, the Diwali bonus and the
    recurring monthly bills, then derives quantiles from rolling-origin
    backtest residuals.

    ISSUE-03: implement `predict`.  The CLI switches to this class with
    `--model receivables`; until then `make submit` uses the baseline.
    """

    max_horizon_weeks: int = 13

    def predict(
        self,
        bundle: DataBundle,
        as_of: pd.Timestamp,
        horizon_weeks: int = 13,
    ) -> pd.DataFrame:
        raise NotImplementedError("ISSUE-03: implement the invoice-level cash forecaster")
