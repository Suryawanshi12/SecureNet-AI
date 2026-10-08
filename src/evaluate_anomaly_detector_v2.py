import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix, classification_report

print("Loading Isolation Forest V2...")
model = joblib.load("models/isolation_forest_model_v2.pkl")
print("Isolation Forest V2 loaded!")

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
#
# Isolation Forest:
#  1  = Normal
# -1  = Anomaly
# --------------------------------------------------

print("\nDetecting anomalies...")

predictions = model.predict(X_test)

print("Anomaly detection completed!")

# Convert:
# Normal  -> 0
# Anomaly -> 1

y_pred = (predictions == -1).astype(int)

# --------------------------------------------------
# Actual labels
#
# BENIGN (0) = Normal
# Any attack = Anomaly
# --------------------------------------------------

y_actual = (y_test != 0).astype(int)

# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n======================================")
print("ANOMALY DETECTION V2 RESULTS")
print("======================================")

total = len(y_pred)

normal_count = (y_pred == 0).sum()
anomaly_count = (y_pred == 1).sum()

print("\nTotal samples:", total)
print("Predicted Normal:", normal_count)
print("Predicted Anomaly:", anomaly_count)

print(
    f"\nAnomaly Rate: {(anomaly_count / total) * 100:.2f}%"
)

# --------------------------------------------------
# Classification Report
# --------------------------------------------------

print("\nClassification Report:\n")

report = classification_report(
    y_actual,
    y_pred,
    target_names=["Normal", "Anomaly"],
    zero_division=0
)

print(report)

# --------------------------------------------------
# Confusion Matrix
# --------------------------------------------------

cm = confusion_matrix(y_actual, y_pred)

print("\nConfusion Matrix:")
print(cm)

# --------------------------------------------------
# Additional metrics
# --------------------------------------------------

tn, fp, fn, tp = cm.ravel()

print("\n======================================")
print("DETAILED METRICS")
print("======================================")

print("True Negatives :", tn)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Positives :", tp)

print(
    f"\nAttack Detection Rate (Recall): "
    f"{(tp / (tp + fn)) * 100:.2f}%"
)

print(
    f"False Positive Rate: "
    f"{(fp / (fp + tn)) * 100:.2f}%"
)

print("\n======================================")
print("ANOMALY V2 EVALUATION COMPLETED!")
print("======================================")
