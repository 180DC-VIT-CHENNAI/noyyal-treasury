# Scoring and the judge's simulator

This page explains how the 100 points are allocated, what is automated, and the
exact simulator rule the judge uses. The organiser engine and its hidden data
are private; the formulas here are enough to reason about the trade-offs.

## The 100 points

| Category | Points | Metric | Mode |
|---|---:|---|---|
| Core accuracy | 9 | Inflow WAPE = Σ\|actual − p50\| / Σ\|actual\| over 13 weeks | automated |
| | 6 | Outflow WAPE, same formula | automated |
| | 7 | Mean pinball loss of `closing_p10/p50/p90` | automated |
| | 3 | 80% interval coverage: full at \|coverage − 0.8\| ≤ 0.1, zero at 0.4 | automated |
| Financial outcome | 25 | 13-week treasury cost from the simulator using `buffer_plan.csv` (lower is better) | automated |
| Robustness | 5 | Sister company at two as-of dates: valid, schema-correct output in under 120 s | automated |
| | 5 | Normalised inflow WAPE averaged over the two sister origins | automated |
| Engineering | 10 | Hidden tests (FX, dedupe, repair, calendar, simulator, interfaces) | automated |
| | 3 | `ruff` and `mypy` on `src/noyyal` | automated |
| | 2 | Human review of `forecast/receivables.py` and `policy/buffer.py` | human |
| Business judgment | 12 | Memo rubric (four items × 0–3) | semi-automated + human |
| | 8 | Five-minute defence | human |
| Reproducibility & docs | 3 | Clean-room `make submit` reproduces the submitted files within 0.1% | automated |
| | 2 | README run steps and three slide titles present | semi-automated |
| **Total** | **100** | 76 automated · 14 semi-automated · 10 human | |

### Normalisation

Each automated metric is converted to points with the same anchors. The
organisers compute the anchors by running three policies through the scorer:
the **floor** (a trivial policy), the **baseline** shipped in this repository,
and the **reference** solution.

```python
def normalise(m, floor, base, ref, higher_is_better=True):
    if not higher_is_better:            # flip losses, errors, costs
        m, floor, base, ref = -m, -floor, -base, -ref
    if m <= floor:
        return 0.0
    if m <= base:
        return 0.4 * (m - floor) / (base - floor)
    return min(1.0, 0.4 + 0.6 * (m - base) / (ref - base))
```

Matching the baseline earns 40% of a category; matching the reference earns
100%. Beating the reference only matters in tie-breaks.

## Simulator rule (binding)

For each day in the window:

1. Apply the day's realised operating flows to the current account.
2. If cash is above that week's `min_cash_target_inr`, sweep the excess into
   the liquid fund. It earns 6.4% from the next day.
3. If cash would go negative, request a liquid-fund redemption for the gap
   (arrives T+1) and draw the CC line for the gap today, so the account is back
   to zero. **The target is a sweep threshold, not a borrowing target**: the
   accounts team does not borrow to hold cash above it.
4. At 3 pm each Friday, before wages are paid, if cash plus undrawn CC is less
   than that week's wages, charge ₹50 lakh. Wages are funded by 3 pm.
5. CC interest accrues daily on the drawn balance at 10.25% actual/365. A
   balance above ₹60 crore costs an extra 2%/year; four consecutive days over
   the limit costs a ₹25 lakh covenant penalty.
6. Liquid-fund yield accrues on the prior day's balance.

Treasury cost = CC interest + overdraw interest + penalties − liquid-fund yield.
The scorer uses the hidden realised daily flows; your forecast is not fed back
into the simulator. A gated path (missed wage funding) is still scored, with the
shortfall penalty included.

### Why the buffer decision is a U-curve

A high target keeps cash idle (0% yield) and avoids CC draws. A low target
sweeps more into the liquid fund (6.4%) but takes CC bridge draws at 10.25% and
risks the Friday check. The opening CC headroom is only ₹1.5 crore, so a target
that is too thin can breach the limit in a heavy week. A target that is too high
forgoes yield for no benefit. Backtest a grid on 2025–2026 and keep the
simulated Friday-shortfall probability at or below 2%.

## Submission validation

The engine blocks scoring if any of these fail:

- all three files present; 13 rows with the exact week starts;
- no NaN; `p10 ≤ p50 ≤ p90` for net and closing;
- targets non-negative and at most the CC limit;
- hedge ratios in [0, 1]; forward notional no greater than open receivables per
  currency;
- `manifest.json` hashes match the files.

## Anti-gaming

- Any read of a hidden path or network call during `make submit` is a
  disqualification. The sandbox blocks both and logs attempts.
- The sister-company run exposes a forecast that is a lookup of Noyyal's own
  numbers. The engine also greps for 13-row numeric literals in source.
- Submitted files must match the clean-room rebuild; if not, the core,
  financial and robustness categories are scored on the rebuilt files.
- Tie-breaks: lower raw treasury cost, then better sister-company WAPE, then
  earlier tag.

## What is *not* scored automatically

The memo and the defence are deliberate judgment calls. Defensible answers
include hedging 50–60% in layers (receipt timing is uncertain) or 85–100% of
P50 (the MD's stated risk appetite). What matters is that the ratio is
consistent with your own forecast quantiles and that you price the cost of
being wrong, including Harrowgate concentration and what to ask the bank before
the December review.

## Local checks

```bash
make test            # visible tests; five fail by design
make lint
make typecheck
make submit
```

The hidden suite is a superset of the visible tests. Passing the visible tests
is necessary, not sufficient. The public tests do not contain hidden data.
