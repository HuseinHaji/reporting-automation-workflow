"""Run the complete reporting automation workflow from repo root."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "src/generate_synthetic_data.py",
    "src/validate_data.py",
    "src/transform_data.py",
    "src/calculate_kpis.py",
    "src/generate_reports.py",
    "src/export_powerbi.py",
]


def main() -> None:
    for step in STEPS:
        print(f"Running {step}")
        subprocess.run([sys.executable, step], cwd=ROOT, check=True)
    print("Reporting automation workflow completed.")


if __name__ == "__main__":
    main()
