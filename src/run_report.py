from csv import DictReader, DictWriter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "monthly_input.csv"
OUTPUT_DIR = ROOT / "output"
REQUIRED_FIELDS = ["month", "business_unit", "actual_eur", "plan_eur", "owner"]


def parse_amount(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        label = row.get("business_unit", "unknown")
        raise ValueError(f"{label}: invalid {field}") from exc


def build_row(row):
    actual = parse_amount(row, "actual_eur")
    plan = parse_amount(row, "plan_eur")
    variance = actual - plan
    variance_pct = variance / plan if plan else 0
    status = "review" if abs(variance_pct) > 0.1 else "ok"
    action = "Owner follow-up required" if status == "review" or not row["owner"] else "Ready for reporting"
    return {
        **row,
        "variance_eur": round(variance, 2),
        "variance_pct": round(variance_pct, 3) if plan else "",
        "status": status,
        "action": action,
    }


def validate(row):
    issues = []
    for field in REQUIRED_FIELDS:
        if not row[field]:
            issues.append(("high" if field in {"actual_eur", "plan_eur", "owner"} else "medium", f"Missing {field}"))
    if row["actual_eur"] == "0":
        issues.append(("high", "Actual value is zero"))
    if parse_amount(row, "plan_eur") == 0:
        issues.append(("critical", "Plan value is zero"))
    return issues


def build_unit_scorecard(report_rows):
    grouped = {}
    for row in report_rows:
        bucket = grouped.setdefault(
            row["business_unit"],
            {"business_unit": row["business_unit"], "actual_eur": 0.0, "plan_eur": 0.0, "review_items": 0},
        )
        bucket["actual_eur"] += parse_amount(row, "actual_eur")
        bucket["plan_eur"] += parse_amount(row, "plan_eur")
        bucket["review_items"] += int(row["status"] == "review")

    scorecard = []
    for values in grouped.values():
        variance = values["actual_eur"] - values["plan_eur"]
        scorecard.append(
            {
                "business_unit": values["business_unit"],
                "actual_eur": round(values["actual_eur"], 2),
                "plan_eur": round(values["plan_eur"], 2),
                "variance_eur": round(variance, 2),
                "variance_pct": round(variance / values["plan_eur"], 3) if values["plan_eur"] else "",
                "review_items": values["review_items"],
            }
        )
    return sorted(scorecard, key=lambda item: item["variance_eur"])


def build_control_summary(report_rows, issues):
    actual = sum(parse_amount(row, "actual_eur") for row in report_rows)
    plan = sum(parse_amount(row, "plan_eur") for row in report_rows)
    review_items = sum(row["status"] == "review" for row in report_rows)
    return [
        {
            "rows_processed": len(report_rows),
            "actual_eur": round(actual, 2),
            "plan_eur": round(plan, 2),
            "variance_eur": round(actual - plan, 2),
            "variance_pct": round((actual - plan) / plan, 3) if plan else "",
            "review_items": review_items,
            "quality_issues": len(issues),
            "report_status": "blocked" if issues else "ready",
        }
    ]


def write_csv(path, rows, fieldnames=None):
    if fieldnames is None:
        fieldnames = rows[0].keys() if rows else []
    with path.open("w", newline="") as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INPUT.open(newline="") as file:
        rows = list(DictReader(file))
    missing = [field for field in REQUIRED_FIELDS if rows and field not in rows[0]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    report_rows = [build_row(row) for row in rows]
    issues = [
        {"month": row["month"], "business_unit": row["business_unit"], "severity": severity, "issue": issue}
        for row in rows
        for severity, issue in validate(row)
    ]

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_csv(OUTPUT_DIR / "monthly_report.csv", report_rows)
    write_csv(OUTPUT_DIR / "quality_issues.csv", issues, ["month", "business_unit", "severity", "issue"])
    write_csv(OUTPUT_DIR / "business_unit_scorecard.csv", build_unit_scorecard(report_rows))
    write_csv(OUTPUT_DIR / "control_summary.csv", build_control_summary(report_rows, issues))

    print(f"Wrote report and {len(issues)} quality issues to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
