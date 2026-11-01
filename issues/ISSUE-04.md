# ISSUE-04 · Choose a minimum-cash target that survives the Friday check

**Difficulty:** medium-hard · **Area:** `src/noyyal/policy/buffer.py` · **Tests:** hidden superset

## Context

`plan_buffer()` is a stub and `make submit` falls back to a flat ₹5 crore target.
The target is a sweep threshold: excess cash goes to the liquid fund, and the CC
line bridges the account to zero when flows go negative. The opening CC headroom
is only ₹1.5 crore. A target that is too thin can breach the limit on a heavy
week; a target that is too high forgoes 6.4% yield for no benefit.

## What to change

- Implement `plan_buffer(forecast, terms)` returning 13 rows with non-negative
  targets at or below the CC limit.
- Use the simulator on rolling historical windows to pick a target (or a rule).
- Keep the simulated Friday-shortfall probability at or below 2%.
- Do not tune to a single window; test at least four origins.

## Acceptance

- `plan_buffer` returns the required shape and constraints.
- On a 2025–2026 rolling backtest, your plan's simulated treasury cost beats the
  flat ₹5 crore plan.
- No hard-coded 13-row numeric array; the target must be derived from the
  forecast.
- The hidden simulator cost improves relative to the shipped baseline.

## Hints

The simulator is a U-curve, not a monotone function. Plot cost against a grid of
targets for several windows. A target around the 99th percentile of weekly net
outflows plus a margin is a reasonable starting rule; then backtest it.
