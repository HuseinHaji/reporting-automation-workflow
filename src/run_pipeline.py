from pathlib import Path
from subprocess import run

BASE_PATH = Path(__file__).resolve().parents[1]


def run_step(command):
    print(f'Running: {command}')
    result = run(command, shell=True, cwd=BASE_PATH)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():
    run_step('python src/generate_raw_data.py')
    run_step('python src/validate_data.py')
    run_step('python src/transform_data.py')
    run_step('python src/create_report.py')
    print('Pipeline complete.')

if __name__ == '__main__':
    main()
