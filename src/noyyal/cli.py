from __future__ import annotations

import argparse
import json
import sys

import pandas as pd

from noyyal.forecast.model import CashForecaster
from noyyal.forecast.seasonal_naive import SeasonalNaiveForecaster
from noyyal.hedge.forward import baseline_hedge_book
from noyyal.io.loaders import load_bundle
from noyyal.policy.buffer import DEFAULT_TARGET_INR, flat_buffer
from noyyal.submission import (
    SubmissionError,
    write_buffer,
    write_forecast,
    write_hedge,
    write_submission,
)


def _as_of(value: str) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _hedge_payload(book: pd.DataFrame, ratio: float) -> dict:
    return {
        "hedge_ratio": {"USD": float(ratio), "EUR": float(ratio)},
        "tenor_policy": "SINGLE",
        "forwards": [
            {
                "currency": row.currency,
                "notional_fcy": float(row.notional_fcy),
                "maturity_date": str(pd.Timestamp(row.maturity_date).date()),
            }
            for row in book.itertuples()
        ],
    }


def _forecast(args: argparse.Namespace):
    bundle = load_bundle(args.data)
    as_of = _as_of(args.as_of)
    opening = float(bundle.opening["current_account_inr"])
    if args.model == "receivables":
        try:
            return bundle, CashForecaster().predict(bundle, as_of, args.horizon)
        except NotImplementedError as exc:
            raise SystemExit(f"invoice-level forecaster is not implemented yet: {exc}") from exc
    return bundle, SeasonalNaiveForecaster().predict(bundle.ledger, as_of, opening, args.horizon)


def cmd_forecast(args: argparse.Namespace) -> int:
    bundle, forecast = _forecast(args)
    write_forecast(forecast, args.out)
    print(f"wrote {args.out} ({len(forecast)} weeks, model={args.model})")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    bundle, forecast = _forecast(args)
    plan = flat_buffer(forecast, args.target_inr)
    write_buffer(plan, args.out)
    print(f"wrote {args.out} ({len(plan)} weeks, flat target={args.target_inr:,.0f})")
    return 0


def cmd_hedge(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.data)
    as_of = _as_of(args.as_of)
    book = baseline_hedge_book(bundle.receivables, bundle.fx, as_of, ratio=args.ratio)
    payload = _hedge_payload(book, args.ratio)
    write_hedge(payload, args.out)
    print(f"wrote {args.out} ({len(book)} forward(s), ratio={args.ratio})")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    bundle, forecast = _forecast(args)
    as_of = _as_of(args.as_of)
    plan = flat_buffer(forecast, args.target_inr)
    book = baseline_hedge_book(bundle.receivables, bundle.fx, as_of, ratio=args.ratio)
    payload = _hedge_payload(book, args.ratio)
    try:
        manifest = write_submission(args.out, forecast, plan, payload, bundle.terms, bundle.receivables)
    except SubmissionError as exc:
        print(f"submission invalid: {exc}", file=sys.stderr)
        return 2
    print(f"wrote submission to {args.out}")
    print(json.dumps({"files": manifest["files"], "memo": manifest["memo"]}, indent=2))
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.data)
    summary = {
        "ledger_rows": len(bundle.ledger),
        "ledger_from": str(bundle.ledger["value_date"].min().date()),
        "ledger_to": str(bundle.ledger["value_date"].max().date()),
        "open_receivables": len(bundle.receivables),
        "open_receivables_fcy": {
            currency: round(float(group["amount_fcy"].sum()), 2)
            for currency, group in bundle.receivables.groupby("currency")
        },
        "open_pos": len(bundle.commitments),
        "payroll_weeks": len(bundle.payroll),
        "cc_limit_inr": bundle.terms.cc_limit_inr,
        "opening": bundle.opening,
    }
    print(json.dumps(summary, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="noyyal", description="Noyyal Knits treasury CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--as-of", required=True, help="YYYY-MM-DD forecast origin")
        p.add_argument("--data", default="data/public", help="public data directory")
        p.add_argument("--horizon", type=int, default=13)
        p.add_argument("--model", choices=["seasonal", "receivables"], default="seasonal")
        p.add_argument("--target-inr", type=float, default=DEFAULT_TARGET_INR)
        p.add_argument("--ratio", type=float, default=1.0)

    p_forecast = sub.add_parser("forecast", help="write submission/forecast.csv")
    common(p_forecast)
    p_forecast.add_argument("--out", default="submission/forecast.csv")
    p_forecast.set_defaults(func=cmd_forecast)

    p_plan = sub.add_parser("plan", help="write submission/buffer_plan.csv")
    common(p_plan)
    p_plan.add_argument("--out", default="submission/buffer_plan.csv")
    p_plan.set_defaults(func=cmd_plan)

    p_hedge = sub.add_parser("hedge", help="write submission/hedge.json")
    common(p_hedge)
    p_hedge.add_argument("--out", default="submission/hedge.json")
    p_hedge.set_defaults(func=cmd_hedge)

    p_submit = sub.add_parser("submit", help="write the complete submission directory")
    common(p_submit)
    p_submit.add_argument("--out", default="submission/")
    p_submit.set_defaults(func=cmd_submit)

    p_inspect = sub.add_parser("inspect", help="print a data summary")
    p_inspect.add_argument("--data", default="data/public")
    p_inspect.set_defaults(func=cmd_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
