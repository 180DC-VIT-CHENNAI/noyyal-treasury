# ISSUE-05 · Fix the simulator: actual/365 and T+1 settlement

**Difficulty:** medium · **Area:** `src/noyyal/policy/simulator.py` · **Tests:** `tests/test_simulator.py`

## Context

The shipped simulator has two deliberate defects that make the buffer look
cheaper and safer than it is:

1. Interest is accrued on actual/360, not the sanctioned actual/365.
2. Liquid-fund redemptions are credited the same day. The fund settles T+1, so
   the CC line must bridge the gap for a day.

A third consequence: when a redemption is pending, the CC must bridge the
**full** gap, not `gap − redemption`.

## What to change

- Use `terms.actual_day_basis` (365) for CC interest, overdraw interest and
  liquid yield.
- Queue redemptions for the next business day (weekends and TN bank holidays).
- Draw CC for the full gap today; credit the redemption when it arrives.
- Keep the published target semantics: sweep above the target, CC only to keep
  cash non-negative.

## Acceptance

- `pytest tests/test_simulator.py -q` passes.
- A 10 m opening CC balance accrues `10m × 0.1025 / 365` in one day.
- A 1 m outflow with a 10 m liquid balance leaves the liquid fund at 10 m on
  day 1 and draws 1 m of CC.
- Same seed, same plan → identical results (deterministic).
- Hidden tests for Friday shortfall and the covenant penalty pass.

## Hints

`overdraw_max_days` is three; the fourth consecutive day over the limit is the
covenant breach. The Friday check happens before wages are paid. Do not add a
repayment rule that is not in `docs/SCORING.md`.
