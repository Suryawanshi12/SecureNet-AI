import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

print("Loading training data...")

df = pd.read_csv(
    "data/processed/train_encoded.csv",
    low_memory=False
)

print("Training data loaded!")
print("Total rows:", len(df))

# --------------------------------------------------
# Keep ONLY BENIGN traffic
# Label 0 = BENIGN
# --------------------------------------------------

benign_df = df[df["Label"] == 0].copy()

print("\nBENIGN training samples:", len(benign_df))

X_benign = benign_df.drop(columns=["Label"])

print("BENIGN feature shape:", X_benign.shape)

# --------------------------------------------------
# Create Isolation Forest
# --------------------------------------------------

print("\nCreating Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)

# --------------------------------------------------
# Train only on normal traffic
# --------------------------------------------------

print("Training anomaly detector on BENIGN traffic...")

model.fit(X_benign)

print("Training completed!")

# --------------------------------------------------
# Save model
# --------------------------------------------------

model_path = "models/isolation_forest_model_v2.pkl"

joblib.dump(model, model_path)

print("\nAnomaly detector saved to:")
print(model_path)

print("\n======================================")
print("ANOMALY DETECTOR V2 COMPLETED!")
print("======================================")