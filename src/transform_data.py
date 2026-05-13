import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'
REPORTING_PATH = BASE_PATH / 'data' / 'reporting'


def clean_transactions(df):
    clean = df[df['validation_status'] == 'OK'].copy()
    clean = clean.drop(columns=['validation_status', 'validation_reason'])
    clean['product_group'] = clean['product_group'].fillna('Other')
    clean['status_code'] = clean['status_code'].replace({'': 'UNKNOWN'})
    return clean


def main():
    REPORTING_PATH.mkdir(parents=True, exist_ok=True)
    validated = pd.read_csv(PROCESSED_PATH / 'validated_transactions.csv', parse_dates=['transaction_date'])
    clean = clean_transactions(validated)
    clean.to_csv(REPORTING_PATH / 'clean_reporting_table.csv', index=False)
    print('Clean reporting table saved to', REPORTING_PATH)

if __name__ == '__main__':
    main()
