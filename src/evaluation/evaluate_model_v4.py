import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report

# ==========================================
# 1. Load Model 4
# ==========================================

print("Loading Model 4...")

model = joblib.load("models/xgboost_ids_model_v4.pkl")

print("Model 4 loaded!")


# ==========================================
# 2. Load Test Data
# ==========================================

print("\nLoading test data...")

df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")
print("Rows:", len(df))


# ==========================================
# 3. Separate Features and Target
# ==========================================

X_test = df.drop(columns=["Label"])
y_test = df["Label"]


# ==========================================
# 4. Predictions
# ==========================================

print("\nMaking predictions...")

y_pred = model.predict(X_test)

print("Predictions completed!")


# ==========================================
# 5. Accuracy
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

print("\n======================================")
print("MODEL 4 EVALUATION")
print("======================================")

print(f"\nAccuracy: {accuracy:.4f}")
print(f"Accuracy: {accuracy * 100:.2f}%")


# ==========================================
# 6. Classification Report
# ==========================================

class_names = [
    "BENIGN",
    "Bot",
    "DDoS",
    "DoS GoldenEye",
    "DoS Hulk",
    "FTP-Patator",
    "DoS slowloris",
    "DoS Slowhttptest",
    "Heartbleed",
    "Infiltration",
    "PortScan",
    "SSH-Patator",
    "Web Attack - Brute Force",
    "Web Attack - Sql Injection",
    "Web Attack - XSS"
]

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
        labels=list(range(15)),
        target_names=class_names,
        zero_division=0
    )
)


print("\n======================================")
print("MODEL 4 EVALUATION COMPLETED!")
print("======================================")