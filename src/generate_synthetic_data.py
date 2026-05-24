"""Generate deterministic synthetic raw data for monthly reporting automation."""

import numpy as np
import pandas as pd

from config import RANDOM_SEED, RAW_FILES, ensure_directories

COUNTRIES = ["Germany", "France", "Netherlands", "Austria", "Switzerland"]
INDUSTRIES = ["Insurance", "Banking", "Manufacturing", "Logistics", "Technology", "Healthcare"]
COMPANY_SIZES = ["Small", "Mid-Market", "Enterprise"]
RISK_RATINGS = ["Low", "Medium", "High"]
PRODUCT_LINES = ["Core Policy", "Claims Analytics", "Risk Platform", "Service Desk"]
ACCOUNT_MANAGERS = ["A. Keller", "M. Schneider", "S. Bauer", "L. Weber", "N. Fischer"]
PAYMENT_METHODS = ["Bank Transfer", "SEPA", "Card", "Manual Adjustment"]
CASE_TYPES = ["Claim Review", "Billing Query", "Contract Change", "Service Request"]


def generate_customers(rng: np.random.Generator, count: int = 80) -> pd.DataFrame:
    rows = []
    for idx in range(1, count + 1):
        onboarding = pd.Timestamp("2022-01-01") + pd.Timedelta(days=int(rng.integers(0, 900)))
        risk = rng.choice(RISK_RATINGS, p=[0.48, 0.34, 0.18])
        rows.append(
            {
                "customer_id": f"CUST{idx:04d}",
                "customer_name": f"Client {idx:04d} GmbH",
                "country": rng.choice(COUNTRIES, p=[0.38, 0.18, 0.16, 0.14, 0.14]),
                "industry": rng.choice(INDUSTRIES),
                "company_size": rng.choice(COMPANY_SIZES, p=[0.25, 0.45, 0.30]),
                "risk_rating": risk,
                "account_manager": rng.choice(ACCOUNT_MANAGERS),
                "onboarding_date": onboarding.date(),
                "active_flag": rng.choice(["Y", "N"], p=[0.9, 0.1]),
            }
        )
    return pd.DataFrame(rows)


def generate_contracts(customers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i, customer in customers.iterrows():
        start = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))
        duration = int(rng.choice([365, 548, 730], p=[0.55, 0.25, 0.20]))
        end = start + pd.Timedelta(days=duration)
        product = rng.choice(PRODUCT_LINES)
        rows.append(
            {
                "contract_id": f"CON{i + 1:05d}",
                "customer_id": customer["customer_id"],
                "contract_start_date": start.date(),
                "contract_end_date": end.date(),
                "annual_contract_value": round(float(rng.normal(85000, 32000)), 2),
                "product_line": product,
                "contract_status": "Active" if end >= pd.Timestamp("2025-12-31") else "Expired",
            }
        )
    return pd.DataFrame(rows)


def generate_invoices(customers: pd.DataFrame, contracts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    months = pd.period_range("2025-01", "2025-12", freq="M")
    active_customers = customers[customers["active_flag"] == "Y"]["customer_id"].tolist()
    invoice_idx = 1
    for month in months:
        customer_sample = rng.choice(active_customers, size=55, replace=False)
        for customer_id in customer_sample:
            contract = contracts[contracts["customer_id"] == customer_id].iloc[0]
            invoice_date = month.to_timestamp() + pd.Timedelta(days=int(rng.integers(0, 19)))
            due_date = invoice_date + pd.Timedelta(days=int(rng.choice([14, 30, 45], p=[0.2, 0.65, 0.15])))
            amount = max(450.0, float(rng.normal(contract["annual_contract_value"] / 12, 1800)))
            status = rng.choice(["Paid", "Open"], p=[0.78, 0.22])
            rows.append(
                {
                    "invoice_id": f"INV{invoice_idx:06d}",
                    "customer_id": customer_id,
                    "invoice_date": invoice_date.date(),
                    "due_date": due_date.date(),
                    "invoice_amount": round(amount, 2),
                    "currency": "EUR",
                    "status": status,
                }
            )
            invoice_idx += 1

    rows.append(rows[0].copy())
    rows[-1]["invoice_amount"] = round(rows[-1]["invoice_amount"] * 1.05, 2)
    rows.append(
        {
            "invoice_id": "INV999997",
            "customer_id": "CUST9999",
            "invoice_date": "2025-11-15",
            "due_date": "2025-12-15",
            "invoice_amount": 4200.00,
            "currency": "EUR",
            "status": "Open",
        }
    )
    rows.append(
        {
            "invoice_id": "INV999998",
            "customer_id": customers.iloc[0]["customer_id"],
            "invoice_date": "2025-10-03",
            "due_date": "2025-09-20",
            "invoice_amount": -950.00,
            "currency": "EUR",
            "status": "Open",
        }
    )
    inactive = customers[customers["active_flag"] == "N"].iloc[0]["customer_id"]
    rows.append(
        {
            "invoice_id": "INV999999",
            "customer_id": inactive,
            "invoice_date": "2025-12-04",
            "due_date": "2026-01-03",
            "invoice_amount": 3100.00,
            "currency": "EUR",
            "status": "Open",
        }
    )
    return pd.DataFrame(rows)


def generate_payments(invoices: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    valid_invoices = invoices.drop_duplicates("invoice_id")
    valid_invoices = valid_invoices[valid_invoices["invoice_amount"] > 0].copy()
    for idx, invoice in valid_invoices.iterrows():
        if invoice["status"] != "Paid":
            continue
        due_date = pd.to_datetime(invoice["due_date"])
        invoice_date = pd.to_datetime(invoice["invoice_date"])
        delay = int(rng.normal(20, 14))
        payment_date = invoice_date + pd.Timedelta(days=max(1, delay))
        if rng.random() < 0.18:
            payment_date = due_date + pd.Timedelta(days=int(rng.integers(1, 35)))
        rows.append(
            {
                "payment_id": f"PAY{len(rows) + 1:06d}",
                "invoice_id": invoice["invoice_id"],
                "payment_date": payment_date.date(),
                "payment_amount": round(float(invoice["invoice_amount"]), 2),
                "payment_method": rng.choice(PAYMENT_METHODS, p=[0.55, 0.3, 0.1, 0.05]),
            }
        )
    rows.append(
        {
            "payment_id": "PAY999999",
            "invoice_id": valid_invoices.iloc[3]["invoice_id"],
            "payment_date": "2025-07-15",
            "payment_amount": -200.0,
            "payment_method": "Manual Adjustment",
        }
    )
    return pd.DataFrame(rows)


def generate_cases(customers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(1, 180):
        customer = customers.sample(1, random_state=int(rng.integers(1, 100000))).iloc[0]
        case_date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))
        status = rng.choice(["Open", "Closed", "In Review"], p=[0.24, 0.62, 0.14])
        rows.append(
            {
                "case_id": f"CASE{idx:05d}",
                "customer_id": customer["customer_id"],
                "case_date": case_date.date(),
                "case_type": rng.choice(CASE_TYPES),
                "case_amount": round(max(0, float(rng.normal(2400, 1600))), 2),
                "case_status": status,
            }
        )
    return pd.DataFrame(rows)


def generate_monthly_targets(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for month in pd.period_range("2025-01", "2025-12", freq="M"):
        for country in COUNTRIES:
            for product in PRODUCT_LINES:
                rows.append(
                    {
                        "month": month.start_time.date(),
                        "country": country,
                        "product_line": product,
                        "target_revenue": round(float(rng.normal(85000, 18000)), 2),
                        "target_collection_rate": round(float(rng.uniform(0.82, 0.94)), 3),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_directories()
    rng = np.random.default_rng(RANDOM_SEED)
    customers = generate_customers(rng)
    contracts = generate_contracts(customers, rng)
    invoices = generate_invoices(customers, contracts, rng)
    payments = generate_payments(invoices, rng)
    cases = generate_cases(customers, rng)
    targets = generate_monthly_targets(rng)

    outputs = {
        "customers": customers,
        "contracts": contracts,
        "invoices": invoices,
        "payments": payments,
        "cases": cases,
        "monthly_targets": targets,
    }
    for name, frame in outputs.items():
        frame.to_csv(RAW_FILES[name], index=False)
        print(f"Wrote {len(frame):,} rows to {RAW_FILES[name].relative_to(RAW_FILES[name].parents[2])}")


if __name__ == "__main__":
    main()
