# Contributing

This is a DOOMFORGE 2026 engineering repository. Contributions are judged on
whether they change a number the business would notice, not on commit count.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make test
```

The public data is in `data/public`. Do not edit it; if you need a different
scenario, write a test fixture or a generator in `tests/fixtures/`.

## Pick an issue

The curated issues are in `issues/`. They are ordered roughly by dependency:

- `ISSUE-01` FX conversion (easy, unblocks the invoice model)
- `ISSUE-02` ledger cleaning (medium)
- `ISSUE-03` invoice-level receipts and bonus calendar (core, hard)
- `ISSUE-04` buffer policy (medium-hard)
- `ISSUE-05` simulator correctness (medium)
- `ISSUE-06` hedge book, API and dashboard (medium)
- `ISSUE-07` backtest, benchmark and CI hygiene (easy)

If you have a better idea, open an issue first and explain the business impact.

## Branch and PR

```bash
git switch -c feat/issue-03-invoice-receipts
# code, tests, docs
make test lint typecheck
git push -u origin feat/issue-03-invoice-receipts
```

Open a pull request using the template. A useful PR:

- links the issue;
- shows the failing test before and the passing test after, or a before/after
  metric (WAPE, coverage, simulated cost);
- keeps the change scoped to one idea;
- does not edit the test expectations to make a defect disappear;
- does not commit generated submission files or hidden data;
- updates the README or docstring when the behaviour changes.

Small PRs are welcome. A 20-line fix with a test beats a 2,000-line rewrite.
Do not submit multiple trivial PRs to farm points; the judges review the diff.

## Code style

- Python 3.11, `ruff` and `mypy` clean (`make lint typecheck`).
- Type hints on public functions; dataclasses for config.
- No new runtime dependency without a reason; no network calls.
- Keep the CLI contract (`noyyal submit --as-of ... --data ... --out ...`).
- Do not hard-code dates, amounts, week counts, or hidden answers.

## Tests

Visible tests are in `tests/`. The hidden suite adds edge cases around the
traps in `docs/DATA_DICTIONARY.md`. Write tests for the defect you fix, not just
for the happy path.

## Security

The judged run executes your code in a container with no network and a
read-only filesystem. Do not attempt to read hidden data, inspect the scorer, or
write outside the output directory. Attempts are logged and disqualify the
submission.

## Licence

By contributing you agree that your contribution is licensed under the MIT
licence in `LICENSE`.
