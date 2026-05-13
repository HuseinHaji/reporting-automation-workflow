import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
REPORTING_PATH = BASE_PATH / 'data' / 'reporting'
LOG_PATH = BASE_PATH / 'reports'


def create_summaries(clean):
    monthly = clean.copy()
    monthly['month_key'] = monthly['transaction_date'].dt.to_period('M').astype(str)
    monthly_summary = (
        monthly.groupby(['month_key', 'business_unit'], as_index=False)['amount'].sum()
        .rename(columns={'amount': 'total_amount'})
    )
    segment_summary = (
        monthly.groupby('segment', as_index=False)['amount'].sum()
        .rename(columns={'amount': 'segment_amount'})
    )
    return monthly_summary, segment_summary


def write_summary(monthly_summary, clean):
    monthly_summary.to_csv(REPORTING_PATH / 'monthly_summary.csv', index=False)
    clean[['business_unit', 'region', 'segment']].drop_duplicates().to_csv(
        REPORTING_PATH / 'business_metadata.csv', index=False
    )
    with open(LOG_PATH / 'executive_summary.txt', 'w', encoding='utf-8') as handle:
        total_amount = clean['amount'].sum()
        total_records = len(clean)
        handle.write('Executive summary for automated reporting workflow\n')
        handle.write(f'Total clean reportable amount: EUR {total_amount:,.2f}\n')
        handle.write(f'Total clean records: {total_records}\n')
        handle.write('Monthly reporting file output is available in data/reporting/monthly_summary.csv.\n')


def main():
    clean = pd.read_csv(REPORTING_PATH / 'clean_reporting_table.csv', parse_dates=['transaction_date'])
    monthly_summary, _ = create_summaries(clean)
    write_summary(monthly_summary, clean)
    print('Reporting outputs created in', REPORTING_PATH)


if __name__ == '__main__':
    main()
