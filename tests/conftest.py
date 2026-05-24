import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def generated_reporting_outputs():
    subprocess.run([sys.executable, "src/run_pipeline.py"], cwd=ROOT, check=True, capture_output=True, text=True)
