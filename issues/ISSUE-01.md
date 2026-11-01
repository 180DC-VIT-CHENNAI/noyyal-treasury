# ISSUE-01 · FX conversion uses the wrong rate and the wrong EUR operation

**Difficulty:** easy · **Area:** `src/noyyal/io/fx.py` · **Tests:** `tests/test_fx.py`

## Context

`to_inr()` is the conversion helper every invoice-level receipt and every
forward P&L calculation depends on. It currently prices settled transactions at
the 3-month forward and divides on the EUR path. Both are wrong. The visible
test fails on the starter.

## What to change

- Use `spot_rate()` for settled amounts.
- Multiply by the spot rate for both USD and EUR.
- Keep `forward_rate()` for the hedge book only.
- Do not change the public signature.

## Acceptance

- `pytest tests/test_fx.py -q` passes (both tests).
- A 10,000 USD receipt on 2026-07-31 equals `10,000 × usdinr_spot`, not the
  forward rate.
- A 10,000 EUR receipt equals `10,000 × eurinr_spot`.
- `make lint typecheck` stays clean.

## Hints

The bug is two lines. The EUR error is an operator, not a rate. Run a quick
assertion against `fx_daily.csv` before and after.
