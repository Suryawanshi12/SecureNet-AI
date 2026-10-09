import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

print("Loading BENIGN training data...")

df = pd.read_csv(
    "data/processed/anomaly_train_benign.csv",
    low_memory=False
)

print("Data loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

X = df.drop(columns=["Label"])

print("\nFeature shape:", X.shape)

print("\nCreating Isolation Forest V3...")

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)

print("Training anomaly detector...")

model.fit(X)

print("\nTraining completed!")

model_path = "models/isolation_forest_model_v3.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:")
print(model_path)

print("\n======================================")
print("ANOMALY DETECTOR V3 TRAINING COMPLETED!")
print("======================================")