"""
src/data/prepare.py

Prepare the Telco Churn dataset for training:
  1. Load the raw CSV and validate it with the Pandera schema.
  2. Fix TotalCharges (impute 0 where tenure == 0, NO row dropping).
  3. Split into train / val / test with stratification.
  4. Build a ColumnTransformer:
       - binary categoricals  -> OrdinalEncoder
       - multi-class cats     -> OneHotEncoder
       - numeric              -> StandardScaler
  5. Fit on train only, transform val and test.
  6. Serialize the fitted preprocessor with joblib.

Usage:
    python -m src.data.prepare
    # or
    python src/data/prepare.py
    # or from another module
    from src.data.prepare import prepare_data
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running as `python src/data/prepare.py` (adds project root to sys.path)
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.data.validate import TelcoSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / \
    "telco_churn.csv"
MODELS_DIR = PROJECT_ROOT / "models"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"

RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# Column groups (explicit, ordered, deterministic)
# ---------------------------------------------------------------------------
NUM_COLS = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]

BINARY_CAT_COLS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "PaperlessBilling",
]

MULTI_CAT_COLS = [
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaymentMethod",
]


# ---------------------------------------------------------------------------
# Step 1 — Load, validate, fix
# ---------------------------------------------------------------------------
def load_and_clean(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load raw CSV, validate it, and return a cleaned DataFrame."""
    df = pd.read_csv(path)

    # Gate 1: raw data must match the schema (before any transformation)
    TelcoSchema.validate(df)

    # Fix TotalCharges: the 11 blanks correspond to tenure == 0 (new customers).
    # Impute them with 0 instead of dropping the rows.
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df.loc[df["tenure"] == 0, "TotalCharges"] = 0.0

    # customerID is an identifier, not a feature
    df = df.drop(columns=["customerID"])

    return df


# ---------------------------------------------------------------------------
# Step 2 — Build the preprocessor
# ---------------------------------------------------------------------------
def build_preprocessor() -> ColumnTransformer:
    """Build the unfitted ColumnTransformer."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "binary",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value", unknown_value=-1),
                BINARY_CAT_COLS,
            ),
            (
                "multi",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                MULTI_CAT_COLS,
            ),
            (
                "num",
                StandardScaler(),
                NUM_COLS
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    preprocessor.set_output(transform="pandas")
    return preprocessor


# ---------------------------------------------------------------------------
# Step 3 — Full pipeline
# ---------------------------------------------------------------------------
def prepare_data(
    path: Path = DATA_PATH,
    val_size: float = 0.15,
    test_size: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Full preparation pipeline.

    Returns
    -------
    X_train, X_val, X_test, y_train, y_val, y_test
    """
    df = load_and_clean(path)

    X = df.drop(columns=["Churn"])
    y = df["Churn"].map({"Yes": 1, "No": 0}).astype(int)

    # First split: train vs (val + test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(val_size + test_size),
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Second split: val vs test (from the temp set)
    relative_test = test_size / (val_size + test_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=relative_test,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    preprocessor = build_preprocessor()

    # Fit on train only, then transform val / test
    X_train = preprocessor.fit_transform(X_train)
    X_val = preprocessor.transform(X_val)
    X_test = preprocessor.transform(X_test)

    # Persist the fitted preprocessor
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    logger.info("Preprocessor saved to %s", PREPROCESSOR_PATH)

    logger.info(
        "Split sizes — train: %d, val: %d, test: %d | features: %d",
        len(X_train), len(X_val), len(X_test), X_train.shape[1],
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


# ---------------------------------------------------------------------------
# Step 4 — Script entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s | %(message)s")
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_data()
    print(
        f"\nShapes — train: {X_train.shape}, val: {X_val.shape}, test: {X_test.shape}")
    print(
        f"Churn rate — train: {y_train.mean():.3f}, "
        f"val: {y_val.mean():.3f}, test: {y_test.mean():.3f}"
    )
