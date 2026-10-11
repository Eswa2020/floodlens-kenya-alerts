import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("FLOODLENS_MODE", "stub")


@pytest.fixture(autouse=True)
def _clean_store():
    from services.reports import store
    store.reset()
    yield
    store.reset()
