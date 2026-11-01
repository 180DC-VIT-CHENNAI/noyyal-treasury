# ISSUE-08 · Harden edge cases and the clean-room rebuild

**Difficulty:** medium · **Area:** `tests/`, `submission.py`, `Makefile`

## Context

The hidden suite contains edge cases the visible tests do not: T+1 across a
weekend, a redemption that spans a bank holiday, duplicate wage rows with
identical amounts, a short-paid EUR invoice, and a submission whose quantiles
are ordered but the week starts are wrong. A clean-room rebuild must reproduce
the submitted files.

## What to change

- Add tests for:
  - T+1 when the next business day is a Monday or a TN holiday;
  - a genuine wage repeat on a different Friday surviving dedupe;
  - a blank-currency EUR receipt and a Jan–Mar 2024 EUR rate repair;
  - `validate_forecast` rejecting wrong week starts and unordered quantiles;
  - `make submit` producing byte-stable files on a rerun.
- Add a `make clean-room` target that copies the repo to a temp directory,
  runs `submit`, and compares values within ₹1,000 / 0.1%.
- Keep the tests offline and under 10 seconds.

## Acceptance

- The new tests pass on a correct implementation and fail on the starter.
- `make clean-room` exits non-zero on a mismatch and prints the differing rows.
- No hidden data is read.
- The PR describes the two edge cases that were previously untested.

## Hints

`submission.py` already computes SHA-256 hashes. For float comparisons, sort by
`week_start` and compare with a tolerance rather than exact string equality.
