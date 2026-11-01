import pandas as pd


def test_public_files_load(bundle):
    assert len(bundle.ledger) > 5_000
    assert len(bundle.receivables) > 0
    assert len(bundle.commitments) > 0
    assert bundle.opening["current_account_inr"] > 0
    assert bundle.terms.cc_limit_inr == 600_000_000


def test_ledger_dates_and_accounts(bundle):
    assert pd.api.types.is_datetime64_any_dtype(bundle.ledger["value_date"])
    assert set(bundle.ledger["account"].unique()) <= {"CURRENT", "CC", "LIQUID"}
    assert set(bundle.ledger["direction"].unique()) <= {"IN", "OUT"}


def test_open_receivables_are_open(bundle):
    assert len(bundle.receivables) > 150
    assert bundle.receivables["due_date"].notna().all()
    assert bundle.receivables["amount_fcy"].min() > 0


def test_facility_terms_match_sanction(bundle):
    assert bundle.terms.cc_rate == 0.1025
    assert bundle.terms.liquid_settlement_days == 1
    assert bundle.terms.shortfall_penalty_inr == 5_000_000
