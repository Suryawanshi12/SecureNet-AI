import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

print("Loading training data...")

df = pd.read_csv(
    "data/processed/train_encoded.csv",
    low_memory=False
)

print("Training data loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Separate features and labels
X = df.drop(columns=["Label"])

print("\nFeatures shape:", X.shape)

# --------------------------------------------------
# Train Isolation Forest
# --------------------------------------------------

print("\nCreating Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)

print("Training anomaly detector...")

model.fit(X)

print("Training completed!")

# --------------------------------------------------
# Save model
# --------------------------------------------------

model_path = "models/isolation_forest_model.pkl"

joblib.dump(model, model_path)

print("\nAnomaly detector saved to:")
print(model_path)

print("\n======================================")
print("ANOMALY DETECTOR TRAINING COMPLETED!")
print("======================================")