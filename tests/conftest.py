from pathlib import Path

import pytest

from noyyal.io.loaders import load_bundle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public"


@pytest.fixture(scope="session")
def bundle():
    return load_bundle(DATA)


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return DATA
