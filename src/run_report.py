from csv import DictReader, DictWriter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "monthly_input.csv"
OUTPUT_DIR = ROOT / "output"


def build_row(row):
    actual = float(row["actual_eur"])
    plan = float(row["plan_eur"])
    variance = actual - plan
    return {
        **row,
        "variance_eur": round(variance, 2),
        "variance_pct": round(variance / plan, 3) if plan else "",
        "status": "review" if abs(variance / plan) > 0.1 else "ok",
    }


def validate(row):
    issues = []
    for field in ["month", "business_unit", "actual_eur", "plan_eur", "owner"]:
        if not row[field]:
            issues.append(f"Missing {field}")
    if row["actual_eur"] == "0":
        issues.append("Actual value is zero")
    return issues


def main():
    with INPUT.open(newline="") as file:
        rows = list(DictReader(file))

    report_rows = [build_row(row) for row in rows]
    issues = [
        {"month": row["month"], "business_unit": row["business_unit"], "issue": issue}
        for row in rows
        for issue in validate(row)
    ]

    OUTPUT_DIR.mkdir(exist_ok=True)
    with (OUTPUT_DIR / "monthly_report.csv").open("w", newline="") as file:
        writer = DictWriter(file, fieldnames=report_rows[0].keys())
        writer.writeheader()
        writer.writerows(report_rows)

    with (OUTPUT_DIR / "quality_issues.csv").open("w", newline="") as file:
        writer = DictWriter(file, fieldnames=["month", "business_unit", "issue"])
        writer.writeheader()
        writer.writerows(issues)

    print(f"Wrote report and {len(issues)} quality issues to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

