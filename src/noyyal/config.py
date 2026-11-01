from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FacilityTerms:
    """Terms of the cash-credit and liquid-fund facilities."""

    cc_limit_inr: float
    cc_rate: float
    overdraw_extra_rate: float
    overdraw_max_days: int
    liquid_yield: float
    liquid_settlement_days: int
    shortfall_penalty_inr: float
    covenant_breach_penalty_inr: float
    actual_day_basis: int

    @classmethod
    def from_dict(cls, payload: dict) -> FacilityTerms:
        return cls(
            cc_limit_inr=float(payload["cc_limit_inr"]),
            cc_rate=float(payload["cc_rate"]),
            overdraw_extra_rate=float(payload["overdraw_extra_rate"]),
            overdraw_max_days=int(payload["overdraw_max_days"]),
            liquid_yield=float(payload["liquid_yield"]),
            liquid_settlement_days=int(payload["liquid_settlement_days"]),
            shortfall_penalty_inr=float(payload["shortfall_penalty_inr"]),
            covenant_breach_penalty_inr=float(payload["covenant_breach_penalty_inr"]),
            actual_day_basis=int(payload["actual_day_basis"]),
        )

    @classmethod
    def load(cls, path: str | Path) -> FacilityTerms:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
