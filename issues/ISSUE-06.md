# ISSUE-06 · Hedge book, forecast API and treasury dashboard

**Difficulty:** medium · **Area:** `hedge/`, `api/`, `ui/` · **Tests:** hidden superset

## Context

The MD allows plain forwards only and wants a defensible hedge ratio. The
service and dashboard are shells: `POST /forecast` returns 501 and the Streamlit
page has empty chart slots.

## What to change

- Implement `hedge_book()` as a layered plain-forward book (for example 1-month
  and 3-month layers), with total notional no greater than open receivables per
  currency.
- Implement `hedge_pnl()` and show the P&L under ±3% FX in the memo.
- Implement `POST /forecast` to return the 13 weekly rows for an `as_of` date.
- Wire the Streamlit fan and buffer chart to the current submission.

## Acceptance

- `hedge.json` satisfies the schema and the notional cap.
- The hedge ratio is consistent with your own forecast quantiles; the memo
  prices the cost of being wrong.
- `POST /forecast` returns 200 with 13 rows; `GET /health` stays 200.
- `streamlit run ui/app.py` starts and renders both charts without an exception.
- Hidden API contract tests pass.

## Hints

A 50–60% layered book and an 85–100% P50 book are both defensible. The rubric
penalises a ratio with no reference to receipt timing or Harrowgate
concentration. For the API, load once at start-up; do not refit per request.
