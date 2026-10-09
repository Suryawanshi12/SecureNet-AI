import pandas as pd
import joblib
from xgboost import XGBClassifier

print("Loading training data...")

df = pd.read_csv(
    "data/processed/train_balanced.csv",
    low_memory=False
)

print("Data loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

X = df.drop(columns=["Label"])
y = df["Label"]

print("\nFeatures:", X.shape)
print("Target:", y.shape)

print("\nClass distribution:")
print(y.value_counts().sort_index())


# ==========================================
# Targeted class weights
# ==========================================

class_weights = {
    0: 1.0,    # BENIGN
    1: 1.0,    # Bot
    2: 1.0,    # DDoS
    3: 1.0,    # DoS GoldenEye
    4: 1.0,    # DoS Hulk
    5: 1.0,    # FTP-Patator
    6: 1.0,    # DoS slowloris
    7: 1.0,    # DoS Slowhttptest
    8: 1.0,    # Heartbleed
    9: 1.0,    # Infiltration
    10: 1.0,   # PortScan
    11: 1.0,   # SSH-Patator

    # Focus on web attacks
    12: 1.5,   # Web Attack - Brute Force
    13: 2.0,   # Web Attack - Sql Injection
    14: 2.5    # Web Attack - XSS
}

sample_weights = y.map(class_weights)

print("\nTargeted class weights:")
for label, weight in class_weights.items():
    print(f"Class {label}: {weight}")


# ==========================================
# Create XGBoost Model
# ==========================================

print("\nCreating XGBoost model...")

model = XGBClassifier(
    objective="multi:softprob",
    num_class=15,

    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,

    subsample=0.8,
    colsample_bytree=0.8,

    tree_method="hist",
    eval_metric="mlogloss",

    random_state=42,
    n_jobs=-1
)


# ==========================================
# Train
# ==========================================

print("\nTraining Model 4...")

model.fit(
    X,
    y,
    sample_weight=sample_weights
)

print("\nTraining completed!")


# ==========================================
# Save Model 4
# ==========================================

model_path = "models/xgboost_ids_model_v4.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:")
print(model_path)

print("\n======================================")
print("XGBOOST MODEL 4 COMPLETED!")
print("======================================")