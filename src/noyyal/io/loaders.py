from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from noyyal.config import FacilityTerms

DATE_COLUMNS = {
    "bank_ledger.csv": ["value_date", "post_date"],
    "receivables_open.csv": ["invoice_date", "bl_date", "due_date", "erp_expected_pay_date"],
    "invoice_payment_history.csv": ["bl_date", "due_date", "paid_date"],
    "purchase_commitments.csv": ["expected_delivery"],
    "payroll.csv": ["week_start", "paid_on"],
    "bonus_history.csv": ["paid_date"],
    "gst_refunds.csv": ["filed_date", "sanctioned_date", "received_date"],
    "fx_daily.csv": ["date"],
    "calendar.csv": ["date"],
}

DATE_FILES = set(DATE_COLUMNS)


@dataclass
class DataBundle:
    ledger: pd.DataFrame
    receivables: pd.DataFrame
    payment_history: pd.DataFrame
    buyers: pd.DataFrame
    commitments: pd.DataFrame
    payroll: pd.DataFrame
    bonus_history: pd.DataFrame
    gst: pd.DataFrame
    fx: pd.DataFrame
    calendar: pd.DataFrame
    terms: FacilityTerms
    opening: dict


def _read(path: Path, name: str) -> pd.DataFrame:
    frame = pd.read_csv(path / name)
    for column in DATE_COLUMNS.get(name, []):
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def load_ledger(data_dir: str | Path) -> pd.DataFrame:
    frame = _read(Path(data_dir), "bank_ledger.csv")
    frame["amount_inr"] = pd.to_numeric(frame["amount_inr"], errors="coerce")
    frame["amount_fcy"] = pd.to_numeric(frame["amount_fcy"], errors="coerce")
    frame["fx_rate_applied"] = pd.to_numeric(frame["fx_rate_applied"], errors="coerce")
    return frame


def load_fx(data_dir: str | Path) -> pd.DataFrame:
    frame = _read(Path(data_dir), "fx_daily.csv").sort_values("date").reset_index(drop=True)
    return frame


def load_bundle(data_dir: str | Path) -> DataBundle:
    """Load every public file.  Dates are pandas Timestamps; money is float."""
    root = Path(data_dir)
    terms = FacilityTerms.load(root / "facility_terms.json")
    opening = json.loads((root / "opening_position.json").read_text(encoding="utf-8"))
    bundle = DataBundle(
        ledger=load_ledger(root),
        receivables=_read(root, "receivables_open.csv"),
        payment_history=_read(root, "invoice_payment_history.csv"),
        buyers=_read(root, "buyers.csv"),
        commitments=_read(root, "purchase_commitments.csv"),
        payroll=_read(root, "payroll.csv"),
        bonus_history=_read(root, "bonus_history.csv"),
        gst=_read(root, "gst_refunds.csv"),
        fx=load_fx(root),
        calendar=_read(root, "calendar.csv"),
        terms=terms,
        opening=opening,
    )
    if bundle.fx.empty:
        raise ValueError("fx_daily.csv is empty")
    return bundle
