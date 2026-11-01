from __future__ import annotations

import pandas as pd


def repair_blank_currency(ledger: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    """Repair export receipts whose currency is blank.

    In 1.5% of export receipts the bank feed dropped the currency and put the
    foreign-currency figure into amount_inr (for example 38,400 instead of
    roughly Rs 32 lakh).  The invoice history and fx_daily.csv are enough to
    repair both the currency and the rupee amount.

    A second defect is narrower: EUR receipts in Jan-Mar 2024 were converted at
    the USD rate.  Detect them against fx_daily.csv and repair them too.

    ISSUE-02: implement this.  Return a copy; do not mutate the input.
    """
    raise NotImplementedError("ISSUE-02: implement repair_blank_currency()")
