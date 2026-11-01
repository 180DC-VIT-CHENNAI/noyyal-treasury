from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from noyyal.config import FacilityTerms

FORECAST_COLUMNS = [
    "week_start",
    "inflow_p50_inr",
    "outflow_p50_inr",
    "net_p10_inr",
    "net_p50_inr",
    "net_p90_inr",
    "closing_p10_inr",
    "closing_p50_inr",
    "closing_p90_inr",
]
BUFFER_COLUMNS = ["week_start", "min_cash_target_inr"]
ALLOWED_ACTIONS = {"APPROVE", "CHALLENGE", "REVIEW", "DECLINE"}


class SubmissionError(ValueError):
    pass


def _clean_week_start(frame: pd.DataFrame, column: str = "week_start") -> pd.DataFrame:
    out = frame.copy()
    out[column] = pd.to_datetime(out[column]).dt.normalize()
    return out


def validate_forecast(forecast: pd.DataFrame, horizon_weeks: int = 13) -> None:
    missing = [c for c in FORECAST_COLUMNS if c not in forecast.columns]
    if missing:
        raise SubmissionError(f"forecast is missing columns: {missing}")
    if len(forecast) != horizon_weeks:
        raise SubmissionError(f"forecast must have {horizon_weeks} rows, got {len(forecast)}")
    frame = _clean_week_start(forecast)
    if frame["week_start"].duplicated().any():
        raise SubmissionError("forecast has duplicate week_start values")
    if frame[FORECAST_COLUMNS].isna().any().any():
        raise SubmissionError("forecast contains NaN")
    if not (frame["net_p10_inr"] <= frame["net_p50_inr"]).all():
        raise SubmissionError("net_p10 must be <= net_p50")
    if not (frame["net_p50_inr"] <= frame["net_p90_inr"]).all():
        raise SubmissionError("net_p50 must be <= net_p90")
    if not (frame["closing_p10_inr"] <= frame["closing_p50_inr"]).all():
        raise SubmissionError("closing_p10 must be <= closing_p50")
    if not (frame["closing_p50_inr"] <= frame["closing_p90_inr"]).all():
        raise SubmissionError("closing_p50 must be <= closing_p90")


def validate_buffer(plan: pd.DataFrame, terms: FacilityTerms, horizon_weeks: int = 13) -> None:
    missing = [c for c in BUFFER_COLUMNS if c not in plan.columns]
    if missing:
        raise SubmissionError(f"buffer plan is missing columns: {missing}")
    if len(plan) != horizon_weeks:
        raise SubmissionError(f"buffer plan must have {horizon_weeks} rows, got {len(plan)}")
    frame = _clean_week_start(plan)
    if frame["week_start"].duplicated().any():
        raise SubmissionError("buffer plan has duplicate week_start values")
    if frame["min_cash_target_inr"].isna().any():
        raise SubmissionError("buffer plan contains NaN")
    if (frame["min_cash_target_inr"] < 0).any():
        raise SubmissionError("min_cash_target_inr must be non-negative")
    if (frame["min_cash_target_inr"] > terms.cc_limit_inr).any():
        raise SubmissionError("min_cash_target_inr must not exceed the CC limit")


def validate_hedge(payload: dict, receivables: pd.DataFrame) -> None:
    ratios = payload.get("hedge_ratio", {})
    for currency in ("USD", "EUR"):
        ratio = ratios.get(currency)
        if ratio is None or not (0.0 <= float(ratio) <= 1.0):
            raise SubmissionError(f"hedge_ratio[{currency}] must be in [0, 1]")
    if payload.get("tenor_policy") not in {"SINGLE", "LAYERED"}:
        raise SubmissionError("tenor_policy must be SINGLE or LAYERED")
    open_by_currency = receivables.groupby("currency")["amount_fcy"].sum().to_dict()
    for forward in payload.get("forwards", []):
        currency = forward.get("currency")
        notional = float(forward.get("notional_fcy", 0.0))
        if notional < 0:
            raise SubmissionError("forward notional must be non-negative")
        if notional > float(open_by_currency.get(currency, 0.0)) + 1e-6:
            raise SubmissionError(
                f"{currency} forward notional exceeds open receivables"
            )


def write_forecast(forecast: pd.DataFrame, path: str | Path) -> None:
    frame = _clean_week_start(forecast)[FORECAST_COLUMNS]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d", float_format="%.2f")


def write_buffer(plan: pd.DataFrame, path: str | Path) -> None:
    frame = _clean_week_start(plan)[BUFFER_COLUMNS]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d", float_format="%.2f")


def write_hedge(payload: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    written = dict(payload)
    written["forwards"] = [
        {**row, "maturity_date": str(pd.Timestamp(row["maturity_date"]).date())}
        for row in payload.get("forwards", [])
    ]
    Path(path).write_text(json.dumps(written, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def build_manifest(out_dir: str | Path, case_id: str = "c1-noyyal") -> dict:
    root = Path(out_dir)
    files = {}
    for name in ("forecast.csv", "buffer_plan.csv", "hedge.json"):
        path = root / name
        if path.exists():
            files[str(path.relative_to(root))] = sha256_file(path)
    memo = root / "memo.md"
    slides = root / "slides.pdf"
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "team_id": os.environ.get("NOYYAL_TEAM_ID", "local"),
        "commit": _git_commit(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "entrypoints": {
            "submit": "make submit",
            "api": "uvicorn noyyal.api.app:app",
            "policy": None,
        },
        "files": files,
        "memo": str(memo) if memo.exists() else None,
        "slides": str(slides) if slides.exists() else None,
        "bonus": [],
    }


def write_submission(
    out_dir: str | Path,
    forecast: pd.DataFrame,
    plan: pd.DataFrame,
    hedge_payload: dict,
    terms: FacilityTerms,
    receivables: pd.DataFrame,
) -> dict:
    validate_forecast(forecast)
    validate_buffer(plan, terms)
    validate_hedge(hedge_payload, receivables)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    write_forecast(forecast, root / "forecast.csv")
    write_buffer(plan, root / "buffer_plan.csv")
    write_hedge(hedge_payload, root / "hedge.json")
    manifest = build_manifest(root)
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
