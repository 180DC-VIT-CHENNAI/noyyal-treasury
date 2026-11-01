from __future__ import annotations

import pandas as pd


def estimate_buyer_lateness(payment_history: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Estimate each buyer's payment delay from invoice history.

    The naive ERP field (erp_expected_pay_date) equals due_date and is not a
    forecast.  Use the realised paid_date - due_date distribution instead.
    Harrowgate's delay drifts over time; a recency-weighted estimate beats a
    lifetime average.

    ISSUE-03: implement.  Return one row per buyer with at least:
    buyer_id, mean_late_days, median_late_days, p90_late_days, n_invoices.
    """
    raise NotImplementedError("ISSUE-03: implement estimate_buyer_lateness()")


def expected_receipts(
    receivables: pd.DataFrame,
    payment_history: pd.DataFrame,
    fx: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """Build one expected receipt per open invoice.

    ISSUE-03: implement.  Columns must include invoice_id, buyer_id, currency,
    expected_pay_date, expected_amount_inr.  Convert with spot, not forward, and
    apply the buyer's short-payment rate from history.
    """
    raise NotImplementedError("ISSUE-03: implement expected_receipts()")
