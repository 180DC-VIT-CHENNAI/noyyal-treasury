# ISSUE-02 · Clean the bank feed without deleting real wage transfers

**Difficulty:** medium · **Area:** `src/noyyal/clean/` · **Tests:** hidden superset

## Context

Two defect classes in `bank_ledger.csv` distort the forecast:

1. 0.4% of rows were re-imported after the February 2025 bank migration with a
   new `txn_id` and identical content. They inflate inflows and outflows.
2. 1.5% of export receipts have a blank currency and the foreign figure in
   `amount_inr`; EUR receipts in Jan–Mar 2024 were converted at the USD rate.

`drop_statement_duplicates()` and `repair_blank_currency()` are stubs.

## What to change

- Dedupe on **content**, not `txn_id`. Do not delete genuine weekly wages: they
  repeat an amount on different dates.
- Infer the missing currency from the buyer and repair `amount_inr` from
  `fx_daily.csv` at the value date.
- Repair the Jan–Mar 2024 EUR rows using `eurinr_spot`.
- Return a copy; do not mutate the input frame.
- Keep the original columns and sort by `value_date, txn_id`.

## Acceptance

- No content duplicates remain in the returned ledger.
- The count of `WAGES` rows is unchanged.
- No export receipt has a blank currency; repaired amounts are consistent with
  `amount_fcy × spot − bank charges`.
- EUR rows in Jan–Mar 2024 have `fx_rate_applied ≈ eurinr_spot`.
- The hidden tests for dedupe/currency pass.

## Hints

`CONTENT_COLUMNS` is already listed in `clean/dedupe.py`. `buyers.csv` maps the
counterparty to a currency. `fx_daily.csv` is keyed by date. The blank-currency
rows are obvious once you plot `amount_inr` against invoice history: they are
three orders of magnitude too small.
