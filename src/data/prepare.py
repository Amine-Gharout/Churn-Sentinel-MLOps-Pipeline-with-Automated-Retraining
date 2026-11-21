import os
import joblib
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

df = pd.read_csv('./../data/raw/full_data.csv')
df['TotalCharges'] = pd.to_numeric(
    df['TotalCharges'], errors='coerce').fillna(np.nan)
df = df[~df['TotalCharges'].isna()]
df.drop(columns='customerID', inplace=True, axis=1)

pd.set_option('display.max_columns', 400)
# Link to the dataset: https://www.kaggle.com/datasets/blastchar/telco-customer-churn/data

print(df.shape)
print(df.info())


num_cols = ["tenure", 'MonthlyCharges', 'TotalCharges']
cat_cols_ohe = ['PaymentMethod', 'Contract', 'InternetService']
cat_cols_le = list(set(df.columns) - set(num_cols) -
                   set(cat_cols_ohe) - set(['Churn']))


X = df.drop(columns=['Churn'])
y = df['Churn'].map({'Yes': 1, 'No': 0})
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=40, stratify=y)


preprocessor = ColumnTransformer(
    transformers=[
        ("ohe", OneHotEncoder(handle_unknown="ignore",
         sparse_output=False), cat_cols_ohe),
        ("ord", OrdinalEncoder(handle_unknown="use_encoded_value",
         unknown_value=-1), cat_cols_le),
        ("num", StandardScaler(), num_cols),
    ],
    remainder="drop",
    verbose_feature_names_out=False,
)
preprocessor.set_output(transform="pandas")

X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)


os.makedirs("models", exist_ok=True)
joblib.dump(preprocessor, "models/preprocessor.joblib")

# Vérification : recharger
loaded = joblib.load("models/preprocessor.joblib")
print(loaded)
