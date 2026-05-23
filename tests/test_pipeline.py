import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def test_pipeline_generates_reporting_control_pack():
    result = subprocess.run(
        [sys.executable, "src/run_report.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "quality issues" in result.stdout

    report = read_csv(ROOT / "output" / "monthly_report.csv")
    issues = read_csv(ROOT / "output" / "quality_issues.csv")
    audit = read_csv(ROOT / "output" / "audit_log.csv")
    control = read_csv(ROOT / "output" / "control_summary.csv")

    assert len(report) == 9
    assert len(issues) == 2
    assert {row["step"] for row in audit} == {"extract", "validate", "transform", "publish"}
    assert control[0]["report_status"] == "blocked"
