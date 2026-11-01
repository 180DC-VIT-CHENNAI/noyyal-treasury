# ISSUE-07 · Backtest, benchmark and CI hygiene

**Difficulty:** easy · **Area:** `forecast/base.py`, `benchmarks/`, `.github/`

## Context

The repository has a thin `rolling_origin_backtest` helper and a benchmark that
only times the baseline. There is no comparable before/after evidence for a
model change, and CI should separate the known failing tests from the rest.

## What to change

- Add a `benchmarks/` report that prints WAPE, pinball and coverage for any
  `Forecaster` on at least four 2025 origins.
- Make the CI layout explicit: a green job for the non-defect tests, lint and
  types; a separate allowed-to-fail job for ISSUE-01/03/05.
- Document the exact command a reviewer should run.

## Acceptance

- `python benchmarks/bench_forecast.py --model seasonal` prints four origins
  and the three metrics.
- The green CI job passes on a fresh clone.
- The known-defect job is clearly labelled and does not block merges.
- The README's command list matches the Makefile.

## Hints

Use `forecast_weeks` and `weekly_aggregate` rather than re-implementing week
logic. Keep the benchmark offline and under 60 seconds.
