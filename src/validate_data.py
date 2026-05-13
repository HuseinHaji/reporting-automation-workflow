import pandas as pd
from pathlib import Path
import yaml

BASE_PATH = Path(__file__).resolve().parents[1]
RAW_PATH = BASE_PATH / 'data' / 'raw'
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'
CONFIG_PATH = BASE_PATH / 'config' / 'reporting_config.yaml'


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def validate_transactions(df, config):
    issues = []
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    missing_cols = [c for c in config['validation']['required_columns'] if c not in df.columns]
    if missing_cols:
        raise ValueError(f'Missing required columns: {missing_cols}')
    invalid_date = df['transaction_date'].isna()
    out_of_range = ~df['transaction_date'].between(pd.to_datetime(config['validation']['min_date']), pd.to_datetime(config['validation']['max_date']))
    negative_amount = df['amount'] < 0
    missing_customer = df['customer_id'].astype(str).str.strip() == ''
    duplicate_transaction = df.duplicated(subset=['transaction_id'], keep=False)

    df['validation_status'] = 'OK'
    df.loc[invalid_date | missing_customer | out_of_range | negative_amount | duplicate_transaction, 'validation_status'] = 'REJECTED'
    df['validation_reason'] = ''
    df.loc[invalid_date, 'validation_reason'] = 'invalid_date'
    df.loc[out_of_range, 'validation_reason'] = 'date_out_of_range'
    df.loc[negative_amount, 'validation_reason'] = 'negative_amount'
    df.loc[missing_customer, 'validation_reason'] = 'missing_customer_id'
    df.loc[duplicate_transaction, 'validation_reason'] = 'duplicate_transaction'

    return df


def main():
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
    config = load_config()
    transactions = pd.read_csv(RAW_PATH / 'transactions_raw.csv')
    validated = validate_transactions(transactions, config)
    validation_summary = validated['validation_status'].value_counts().rename_axis('status').reset_index(name='count')
    rejected = validated[validated['validation_status'] == 'REJECTED'].copy()
    validated.to_csv(PROCESSED_PATH / 'validated_transactions.csv', index=False)
    validation_summary.to_csv(PROCESSED_PATH / 'validation_report.csv', index=False)
    rejected.to_csv(PROCESSED_PATH / 'rejected_records.csv', index=False)
    print('Validation completed. Reports are in', PROCESSED_PATH)

if __name__ == '__main__':
    main()
