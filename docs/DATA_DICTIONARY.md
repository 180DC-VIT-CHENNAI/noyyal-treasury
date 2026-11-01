# Data dictionary

All data is synthetic and generated from a fixed seed. Money is in rupees
unless a column ends in `_fcy`; rates are decimals (`0.1025`), not percentages.
Dates are ISO-8601. Weeks start Monday. `ts` columns are IST.

The snapshot is **31 July 2026**. The forecast window is the 13 weeks beginning
**3 August 2026** and ending **1 November 2026**.

## `bank_ledger.csv` (13,916 rows)

| Column | Type | Notes |
|---|---|---|
| `txn_id` | string | Bank feed id; not stable across re-imports |
| `value_date` | date | Economic date |
| `post_date` | date | Ledger date (same as value date in the public extract) |
| `account` | enum | `CURRENT`, `CC`, `LIQUID` |
| `direction` | enum | `IN`, `OUT` |
| `category` | enum | `EXPORT_RECEIPT`, `DOMESTIC_RECEIPT`, `YARN`, `WAGES`, `BONUS`, `POWER`, `FREIGHT`, `GST_PAYMENT`, `GST_REFUND`, `RODTEP`, `INTEREST_CC`, `FUND_SWEEP`, `CAPEX`, `OTHER` |
| `counterparty_id` | string | Buyer, supplier, `PAYROLL`, `BANK`, etc. |
| `amount_inr` | float | Rupees, 2 dp |
| `currency` | string, nullable | `USD`, `EUR` or null for INR |
| `amount_fcy` | float, nullable | Foreign amount |
| `fx_rate_applied` | float, nullable | Rate used by the bank |
| `narration` | string | Free text; invoice or PO id often embedded |

**Defect classes** (find the rows; do not assume they are absent):

1. After the February 2025 bank migration, **0.4% of rows were re-imported**
   with a new `txn_id` but identical content. Dedupe on content, not id.
   Genuine weekly wage transfers repeat the same amount on different dates and
   must survive.
2. **1.5% of export receipts have a blank currency** and `amount_inr` holding
   the foreign figure (for example 38,400 instead of roughly ₹32 lakh).
3. **EUR receipts in Jan–Mar 2024** were converted with the USD rate. The
   invoice history and `fx_daily.csv` contain enough information to repair
   them.
4. **September 2024 power bills are absent** because they were paid from a
   different account. Do not read the gap as seasonality.
5. A **₹7.5 crore capex** in March 2025 is a one-off and should not enter a
   seasonal baseline.
6. `INTEREST_CC` and `FUND_SWEEP` are policy outcomes, not operating flows.
   Exclude them from the core forecast.

## `receivables_open.csv` (364 rows)

| Column | Notes |
|---|---|
| `invoice_id`, `buyer_id` | Keys |
| `currency`, `amount_fcy` | Invoice currency and face amount |
| `invoice_date`, `bl_date`, `due_date` | Bill of lading and contractual due date |
| `incoterm` | `FOB`, `CIF`, `CFR` |
| `erp_expected_pay_date` | **Naive**: equals `due_date`. Compare with `paid_date` in history before trusting it. |

The book includes overdue invoices. A good model estimates the *remaining*
delay conditional on the invoice not having been paid by 31 July.

## `invoice_payment_history.csv` (3,896 rows)

| Column | Notes |
|---|---|
| `invoice_id`, `buyer_id`, `currency`, `amount_fcy` | Invoice |
| `bl_date`, `due_date`, `paid_date` | Realised timing |
| `amount_received_fcy` | After short payment |
| `short_pay_reason` | `QUALITY_CLAIM`, `BANK_CHARGES`, `DISCOUNT`, or null |

Payment lateness is buyer-specific and Harrowgate's delay drifts later over
2025–2026. A lifetime average will lag the regime.

## `buyers.csv` (14 rows)

`buyer_id, name, country, currency, terms_days, credit_insured,
share_of_fy26_sales`. Harrowgate is the largest by share. Terms are 45–120 days;
late payment is common.

## `purchase_commitments.csv` (534 rows)

`po_id, supplier_id, commodity, qty_kg, price_inr_per_kg, expected_delivery,
credit_days`. Includes POs already delivered but not yet paid, because their
payment date is in the forecast window. Value is `qty_kg × price_inr_per_kg`.

Commodities: `COTTON_YARN_30S`, `POLY_YARN`, `DYES`, `ACCESSORIES`. Cotton-yarn
prices are seasonal and have a random walk.

## `payroll.csv` (174 rows)

`week_start, headcount, gross_wages_inr, paid_on`. Wages are paid Friday unless
that Friday is a Tamil Nadu bank holiday, in which case they are paid Thursday.
The Diwali bonus is a separate outflow, not in this file.

## `bonus_history.csv` (3 rows)

`fy, bonus_pct, paid_date, amount_inr`. The statutory minimum is 8.33% of
annual wages. The bonus is paid on the last working Friday at least seven days
before Diwali. **Diwali moves every year**; use `calendar.csv`, not week-of-year
seasonality. The 2026 bonus falls on Friday 30 October.

## `gst_refunds.csv` (83 rows)

`claim_id, filed_date, amount_inr, sanctioned_date, received_date, status`.
Receipt lags are heavy-tailed; 15% of claims take more than 75 days. Null
`received_date` means the claim was still open at the snapshot.

## `fx_daily.csv` (1,218 rows)

`date, usdinr_spot, eurinr_spot, usdinr_fwd_1m, usdinr_fwd_3m, eurinr_fwd_3m`.
Settled receipts convert at **spot** on the receipt date. Forwards are quoted
with forward points; do not use a 3-month forward for a settled transaction.

## `calendar.csv` (1,371 rows)

`date, is_bank_holiday_tn, festival_name`. Covers 2023-04-01 to 2026-12-31.
The 2026 Diwali is 2026-11-08; Pongal, Tamil New Year and the national holidays
are also present.

## `facility_terms.json`

| Field | Value |
|---|---:|
| `cc_limit_inr` | 600,000,000 |
| `cc_rate` | 0.1025 |
| `overdraw_extra_rate` | 0.02 |
| `overdraw_max_days` | 3 |
| `liquid_yield` | 0.064 |
| `liquid_settlement_days` | 1 |
| `shortfall_penalty_inr` | 5,000,000 |
| `covenant_breach_penalty_inr` | 2,500,000 |
| `actual_day_basis` | 365 |

## `opening_position.json`

`as_of`, `current_account_inr` (₹11.6 crore), `cc_drawn_inr` (₹58.5 crore),
`liquid_fund_inr` (₹0). This is the balance the simulator starts from. The CC
headroom is deliberately thin: ₹1.5 crore.

## Sanity checks before you model

- The ledger ends 31 July; no invoice in `receivables_open` has a `bl_date`
  after 31 July.
- Every key is unique within its file except the injected re-imports.
- `amount_inr` should be roughly `amount_fcy × fx_rate_applied` (minus bank
  charges) for export receipts. Violations are the defects above.
- The sum of `share_of_fy26_sales` is 1.0 across buyers.
