# Architecture

## The system in one picture

```
data/public/*.csv ──► io.loaders ──► clean/* ──► features/calendar
                                         │
                                         ▼
                                  forecast/*.py
                          (seasonal baseline, invoice model)
                                         │
                  ┌──────────────────────┼──────────────────────┐
                  ▼                      ▼                      ▼
           policy/buffer.py       policy/simulator.py      hedge/forward.py
                  │                      │                      │
                  └──────────────► submission writer ◄──────────┘
                                         │
                                  submission/*.csv|json
```

The CLI is the contract the judge runs. Everything else is an implementation
detail a team may restructure, provided the CLI and the submission schema keep
working.

## Module responsibilities

| Module | Responsibility | Known debt |
|---|---|---|
| `config.py` | Parse `facility_terms.json` into a frozen dataclass | none |
| `io/loaders.py` | Read every public file with parsed dates and numeric money | no schema versioning |
| `io/fx.py` | Convert foreign amounts to INR | ISSUE-01: wrong tenor, wrong EUR operation |
| `clean/dedupe.py` | Remove statement re-imports without deleting genuine repeats | ISSUE-02: unimplemented |
| `clean/currency.py` | Repair blank-currency and mis-rated receipts | ISSUE-02: unimplemented |
| `features/calendar.py` | Week starts, holidays, next-festival distance | ISSUE-03: festival stub |
| `forecast/base.py` | Weekly aggregation, WAPE, pinball, coverage, backtest | backtest is a thin harness |
| `forecast/seasonal_naive.py` | Shipped floor-level baseline | ignores the open book and the bonus |
| `forecast/receivables.py` | Buyer lateness and invoice-level receipts | ISSUE-03: stubs |
| `forecast/model.py` | Team forecaster | ISSUE-03: stub |
| `policy/simulator.py` | Cash/CC/liquid replay | ISSUE-05: actual/360, T+0 |
| `policy/buffer.py` | Weekly target | ISSUE-04: stub |
| `hedge/forward.py` | Forward book and mark-to-market | ISSUE-06: stubs |
| `api/app.py` | HTTP surface | ISSUE-06: POST /forecast is 501 |
| `cli.py` | Judge-facing commands | no `--model` fallback beyond two choices |

## Design decisions worth knowing

**Weekly, not daily, forecast output.** The judge scores 13 Monday-starting
weeks. The simulator runs daily because the Friday wage check and the T+1
settlement are daily facts. Do not collapse the simulator to weekly.

**Opening position is given.** `opening_position.json` is the account balance
on 31 July 2026. The core forecast's `closing_*` columns are the current-account
balance under business-as-usual flows, *before* the buffer policy. Do not embed
policy decisions in the forecast; the judge evaluates them separately.

**CC interest and fund sweeps are excluded from the core forecast.** They are
policy outcomes, not operating flows. `forecast.base.EXCLUDED_CATEGORIES` is the
single source of truth for this.

**Quantiles are on the closing balance.** The fan is built by cumulating net
quantiles, not by taking weekly quantiles independently. This keeps the p10
path conservative (low inflow + high outflow) and is the shape the judge
expects.

**The baseline is valid by construction.** `make submit` uses
`SeasonalNaiveForecaster`, `flat_buffer`, and `baseline_hedge_book`, none of
which call the unimplemented stubs. A team can always ship something.

## Performance envelope

- 13,916 ledger rows, 364 open invoices, 534 POs: trivial for pandas.
- Target: `flake8`-clean load + forecast < 5 s; `make submit` < 30 s.
- Sister-company robustness run: < 120 s per origin, including process start.
- Do not add a dependency that needs a GPU, a database, or network access.

## Extension points

- Add a `forecast/scenarios.py` that produces daily scenarios from the weekly
  fan if you want to simulate the policy rather than just the forecast.
- Add `forecast/backtest.py` to compare any `Forecaster` implementation on a
  rolling origin; the scoring engine uses the same WAPE/pinball definitions.
- The API can load a persisted forecaster artifact; do not refit inside a
  request.

## Security and judging boundary

Participant code runs in a container with no network and a read-only
filesystem. It never receives the hidden realised flows. The scorer mounts
hidden data only in a separate process. Do not read `../hidden`, do not attempt
to call the network, and do not infer hidden values from the submission format.
