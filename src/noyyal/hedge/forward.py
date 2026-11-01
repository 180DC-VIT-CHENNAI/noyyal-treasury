from __future__ import annotations

import pandas as pd


def baseline_hedge_book(
    receivables: pd.DataFrame,
    fx: pd.DataFrame,
    as_of: pd.Timestamp,
    ratio: float = 1.0,
) -> pd.DataFrame:
    """Shipped baseline: hedge 100% of open receivables at the 3-month forward."""
    latest = fx[pd.to_datetime(fx["date"]) <= as_of].sort_values("date").iloc[-1]
    rows = []
    for currency, column in (("USD", "usdinr_fwd_3m"), ("EUR", "eurinr_fwd_3m")):
        notional = float(
            receivables.loc[receivables["currency"] == currency, "amount_fcy"].sum()
        )
        if notional <= 0:
            continue
        rows.append(
            {
                "forward_id": f"FWD-{currency}-1",
                "currency": currency,
                "notional_fcy": round(notional * ratio, 2),
                "forward_rate": float(latest[column]),
                "maturity_date": (pd.Timestamp(as_of) + pd.Timedelta(days=91)).normalize(),
            }
        )
    return pd.DataFrame(rows)


def hedge_book(
    receivables: pd.DataFrame,
    fx: pd.DataFrame,
    hedge_ratio: dict[str, float],
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """Build a layered plain-forward book.

    ISSUE-06: implement.  A defensible answer is 50-60% of P50 receipts, split
    across a 1-month and a 3-month layer, with total notional no greater than
    open receivables in each currency.
    """
    raise NotImplementedError("ISSUE-06: implement hedge_book()")


def hedge_pnl(book: pd.DataFrame, fx_path: pd.DataFrame) -> float:
    """Mark the forward book to the realised rate path.

    ISSUE-06: implement.  This is shown in the memo, not scored against the
    hidden FX path.
    """
    raise NotImplementedError("ISSUE-06: implement hedge_pnl()")
