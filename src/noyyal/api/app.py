from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Noyyal treasury API", version="0.1.0")


class ForecastRequest(BaseModel):
    as_of: str
    horizon_weeks: int = 13


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/forecast")
def forecast(request: ForecastRequest):
    # ISSUE-06: wire the forecaster and return a list of rows.
    return JSONResponse(
        status_code=501,
        content={"detail": "POST /forecast is not implemented yet"},
    )
