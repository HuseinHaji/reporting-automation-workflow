import numpy as np
import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parents[1] / 'data' / 'raw'
RANDOM_SEED = 2026

CUSTOMERS = [f'CUST{i:03d}' for i in range(1, 61)]
REGIONS = ['North', 'South', 'East', 'West']
BUSINESS_UNITS = ['Wholesale', 'Retail', 'Manufacturing']
SEGMENTS = ['Segment A', 'Segment B', 'Segment C']
STATUS_CODES = ['ACTIVE', 'CLOSED', 'PENDING']
PRODUCT_GROUPS = ['Industrial', 'Office', 'Consumer', 'Logistics']


def generate_transactions(rng):
    rows = []
    period = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    for i in range(1200):
        cust_id = rng.choice(CUSTOMERS)
        transaction_date = rng.choice(period)
        transaction_date_value = pd.to_datetime(transaction_date).date()
        amount = round(rng.normal(4000, 2600), 2)
        amount = -amount if rng.random() < 0.03 else amount
        business_unit = rng.choice(BUSINESS_UNITS)
        region = rng.choice(REGIONS)
        segment = rng.choice(SEGMENTS, p=[0.35, 0.40, 0.25])
        status_code = rng.choice(STATUS_CODES, p=[0.8, 0.15, 0.05])
        rows.append({
            'transaction_id': f'TXN{i+1:05d}',
            'customer_id': cust_id,
            'business_unit': business_unit,
            'region': region,
            'transaction_date': transaction_date_value,
            'amount': amount,
            'status_code': status_code,
            'segment': segment,
            'product_group': rng.choice(PRODUCT_GROUPS),
        })
    # add duplicates and invalid rows
    rows.append(rows[0].copy())
    rows[-1]['transaction_id'] = rows[0]['transaction_id']
    rows.append({
        'transaction_id': 'TXN99999',
        'customer_id': '',
        'business_unit': 'Unknown',
        'region': 'North',
        'transaction_date': pd.NaT,
        'amount': 5000.0,
        'status_code': 'ACTIVE',
        'segment': 'Segment A',
        'product_group': 'Consumer',
    })
    rows.append({
        'transaction_id': 'TXN99998',
        'customer_id': 'CUST001',
        'business_unit': 'Retail',
        'region': 'West',
        'transaction_date': pd.to_datetime('2025-01-15').date(),
        'amount': 1200.0,
        'status_code': 'PENDING',
        'segment': 'Segment C',
        'product_group': 'Office',
    })
    return pd.DataFrame(rows)


def generate_customer_master(rng):
    rows = []
    for cust in CUSTOMERS:
        rows.append({
            'customer_id': cust,
            'customer_name': f'Client {cust[-3:]}',
            'segment': rng.choice(SEGMENTS),
            'region': rng.choice(REGIONS),
            'industry': rng.choice(['Automotive', 'Retail', 'Logistics', 'Consumer', 'Wholesale']),
        })
    return pd.DataFrame(rows)


def main():
    RAW_PATH.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RANDOM_SEED)
    transactions = generate_transactions(rng)
    customer_master = generate_customer_master(rng)
    transactions.to_csv(RAW_PATH / 'transactions_raw.csv', index=False)
    customer_master.to_csv(RAW_PATH / 'customer_master_raw.csv', index=False)
    print('Generated raw reporting data in', RAW_PATH)

if __name__ == '__main__':
    main()
