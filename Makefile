PYTHON ?= python3
export PYTHONPATH := src

.PHONY: install test lint typecheck inspect forecast plan hedge submit api ui bench clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src

inspect:
	$(PYTHON) -m noyyal.cli inspect --data data/public

forecast:
	$(PYTHON) -m noyyal.cli forecast --as-of 2026-07-31 --data data/public --out submission/forecast.csv

plan:
	$(PYTHON) -m noyyal.cli plan --as-of 2026-07-31 --data data/public --out submission/buffer_plan.csv

hedge:
	$(PYTHON) -m noyyal.cli hedge --as-of 2026-07-31 --data data/public --out submission/hedge.json

submit:
	$(PYTHON) -m noyyal.cli submit --as-of 2026-07-31 --data data/public --out submission/

api:
	$(PYTHON) -m uvicorn noyyal.api.app:app --reload --port 8000

ui:
	$(PYTHON) -m streamlit run ui/app.py

bench:
	$(PYTHON) benchmarks/bench_forecast.py

clean:
	rm -rf submission/forecast.csv submission/buffer_plan.csv submission/hedge.json submission/manifest.json .pytest_cache .mypy_cache .ruff_cache
