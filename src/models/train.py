import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = root / "data/raw/telco_churn.csv"

from src.data.prepare import prepare_data

path = root / "data/raw/telco_churn.csv"
train_x, validate_x, test_x, train_y, validate_y, test_y = prepare_data(
    path=path)
print(train_x.head())
