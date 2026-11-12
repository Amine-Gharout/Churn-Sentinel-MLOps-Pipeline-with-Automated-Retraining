import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class TelcoSchema(pa.DataFrameModel):
    # --- Identity ---
    customerID: Series[str] = pa.Field(unique=True)

    # --- Demographics ---
    gender: Series[str] = pa.Field(isin=["Female", "Male"])
    SeniorCitizen: Series[int] = pa.Field(isin=[0, 1])
    Partner: Series[str] = pa.Field(isin=["Yes", "No"])
    Dependents: Series[str] = pa.Field(isin=["Yes", "No"])

    # --- Account ---
    tenure: Series[int] = pa.Field(ge=0, le=72)

    # --- Services ---
    PhoneService: Series[str] = pa.Field(isin=["Yes", "No"])
    MultipleLines: Series[str] = pa.Field(
        isin=["Yes", "No", "No phone service"])
    InternetService: Series[str] = pa.Field(isin=["DSL", "Fiber optic", "No"])
    OnlineSecurity: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])
    OnlineBackup: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])
    DeviceProtection: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])
    TechSupport: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])
    StreamingTV: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])
    StreamingMovies: Series[str] = pa.Field(
        isin=["Yes", "No", "No internet service"])

    # --- Billing ---
    Contract: Series[str] = pa.Field(
        isin=["Month-to-month", "One year", "Two year"])
    PaperlessBilling: Series[str] = pa.Field(isin=["Yes", "No"])
    PaymentMethod: Series[str] = pa.Field(
        isin=[
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ]
    )
    MonthlyCharges: Series[float] = pa.Field(gt=0)
    TotalCharges: Series[str] = pa.Field(nullable=False)

    # --- Target ---
    Churn: Series[str] = pa.Field(isin=["Yes", "No"])

    @pa.dataframe_check
    def total_charges_consistent_with_tenure(cls, df: pd.DataFrame) -> pd.Series:
        is_empty = df["TotalCharges"].str.strip() == ""
        is_new = df["tenure"] == 0
        return ~(is_empty ^ is_new)

    class Config:
        strict = True


df = pd.read_csv('data/raw/full_data.csv')
TelcoSchema.validate(df)
