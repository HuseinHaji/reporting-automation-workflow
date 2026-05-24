import os


def test_sample_transactions_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "transactions_sample.csv")
    assert os.path.exists(path)
