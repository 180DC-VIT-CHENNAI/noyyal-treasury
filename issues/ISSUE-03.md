# ISSUE-03 · Build the invoice-level 13-week forecast and the festival calendar

**Difficulty:** hard · **Area:** `forecast/`, `features/calendar.py` · **Tests:** hidden superset

## Context

The shipped seasonal-naive baseline ignores the open invoice book, the Diwali
bonus, the purchase commitments and buyer-level payment drift. Most of the next
eight weeks of receipts are already invoiced. The core of the case is to
forecast each open invoice's arrival date and each committed outflow.

## What to change

1. `features/calendar.py::days_to_festival` — return the number of days to the
   next named festival, using `calendar.csv`, not week-of-year.
2. `forecast/receivables.py::estimate_buyer_lateness` — per-buyer delay from
   realised `paid_date − due_date`, recency-weighted; Harrowgate's drift needs a
   trend or a recent window.
3. `forecast/receivables.py::expected_receipts` — one expected receipt per open
   invoice, using the *remaining* delay for overdue invoices, the buyer's
   short-pay rate, spot FX and bank charges.
4. `forecast/model.py::CashForecaster.predict` — weekly inflows from receipts,
   domestic receipts and open GST claims; weekly outflows from payroll,
   commitments, the 8.33% Diwali bonus on 30 October, power, GST, freight and
   other recurring bills; quantiles from backtest residuals.
5. Wire `noyyal submit --model receivables`.

## Acceptance

- `days_to_festival(2026-10-30) == 9`, `2026-11-08 == 0`.
- Lateness table has 14 rows; Harrowgate's estimated delay is materially above
  its 2023 average.
- `expected_receipts` returns one row per open invoice with positive amounts and
  expected dates after 31 July 2026.
- `CashForecaster.predict` returns 13 rows with ordered quantiles.
- On a rolling 2025 origin your inflow WAPE beats the seasonal baseline by at
  least 25%; the hidden engine measures the same statistic.
- Do not hard-code the 2026 dates or the hidden window.

## Hints

- The ERP field `erp_expected_pay_date` is just `due_date`; it is a prior, not a
  forecast.
- For an invoice already overdue by `d` days, the expected *remaining* delay is
  not the unconditional mean. Use the historical late distribution or a simple
  survival adjustment.
- Short payments average 1–4%; use the buyer's realised received/face ratio.
- The bonus is 8.33% of trailing 52-week gross wages, paid on the last working
  Friday at least seven days before Diwali.
- Quantiles: bootstrap your own weekly residuals at several origins; do not use
  a fixed ±35% band.
