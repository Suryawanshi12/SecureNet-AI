import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix, classification_report

print("Loading Isolation Forest...")
model = joblib.load("models/isolation_forest_model.pkl")
print("Isolation Forest loaded!")

print("\nLoading test data...")
df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")
print("Rows:", len(df))

X_test = df.drop(columns=["Label"])
y_test = df["Label"]

# --------------------------------------------------
# Predict anomalies
# Isolation Forest:
#  1  = Normal
# -1  = Anomaly
# --------------------------------------------------

print("\nDetecting anomalies...")

anomaly_predictions = model.predict(X_test)

print("Anomaly detection completed!")

# Convert Isolation Forest output:
#  1  -> 0 (Normal)
# -1  -> 1 (Anomaly)

y_anomaly = (anomaly_predictions == -1).astype(int)

# --------------------------------------------------
# Create actual labels
#
# BENIGN = Normal (0)
# Any attack = Anomaly (1)
# --------------------------------------------------

y_actual = (y_test != 0).astype(int)

# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n======================================")
print("ANOMALY DETECTION RESULTS")
print("======================================")

total = len(y_anomaly)

normal_count = (y_anomaly == 0).sum()
anomaly_count = (y_anomaly == 1).sum()

print("\nTotal samples:", total)
print("Predicted Normal:", normal_count)
print("Predicted Anomaly:", anomaly_count)

print(
    f"\nAnomaly Rate: {(anomaly_count / total) * 100:.2f}%"
)

# --------------------------------------------------
# Classification report
# --------------------------------------------------

print("\nClassification Report:")
print(
    classification_report(
        y_actual,
        y_anomaly,
        target_names=["Normal", "Anomaly"],
        zero_division=0
    )
)

# --------------------------------------------------
# Confusion Matrix
# --------------------------------------------------

cm = confusion_matrix(y_actual, y_anomaly)

print("\nConfusion Matrix:")
print(cm)

print("\n======================================")
print("ANOMALY EVALUATION COMPLETED!")
print("======================================")