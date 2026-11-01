from __future__ import annotations

import pandas as pd

CONTENT_COLUMNS = [
    "value_date",
    "post_date",
    "account",
    "direction",
    "category",
    "counterparty_id",
    "amount_inr",
    "currency",
    "amount_fcy",
    "narration",
]


def drop_statement_duplicates(ledger: pd.DataFrame) -> pd.DataFrame:
    """Remove rows re-imported after the February 2025 bank migration.

    The duplicates carry a new txn_id but the same content.  Dedupe on content,
    not on txn_id -- and do not delete genuine repeated wage transfers.  Those
    have the same amount on *different* dates, so a content key that includes
    value_date keeps them.

    ISSUE-02: implement this.  The hidden tests check:
      * every duplicate is removed;
      * the weekly wage rows all survive;
      * the returned frame keeps the original columns and is sorted by date.
    """
    raise NotImplementedError("ISSUE-02: implement drop_statement_duplicates()")
