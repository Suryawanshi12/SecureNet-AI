import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix, classification_report

print("Loading Isolation Forest V3...")

model = joblib.load(
    "models/isolation_forest_model_v3.pkl"
)

print("Model loaded!")

print("\nLoading test data...")

df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")
print("Rows:", len(df))

X_test = df.drop(columns=["Label"])
y_test = df["Label"]

print("\nCalculating anomaly scores...")

scores = model.decision_function(X_test)

print("Anomaly scores calculated!")

# Selected using BENIGN validation data
THRESHOLD = -0.145540

print("\nUsing threshold:", THRESHOLD)

# Score below threshold = anomaly
y_pred = (scores < THRESHOLD).astype(int)

# BENIGN = Normal (0)
# Any attack = Anomaly (1)
y_actual = (y_test != 0).astype(int)

print("\n======================================")
print("ANOMALY DETECTION V3 RESULTS")
print("======================================")

total = len(y_pred)

normal_count = (y_pred == 0).sum()
anomaly_count = (y_pred == 1).sum()

print("\nTotal samples:", total)
print("Predicted Normal:", normal_count)
print("Predicted Anomaly:", anomaly_count)

print(
    f"\nPredicted Anomaly Rate: "
    f"{(anomaly_count / total) * 100:.2f}%"
)

print("\nClassification Report:\n")

print(
    classification_report(
        y_actual,
        y_pred,
        target_names=["Normal", "Anomaly"],
        zero_division=0
    )
)

cm = confusion_matrix(y_actual, y_pred)

print("\nConfusion Matrix:")
print(cm)

tn, fp, fn, tp = cm.ravel()

print("\n======================================")
print("DETAILED METRICS")
print("======================================")

print("True Negatives :", tn)
print("False Positives:", fp)
print("False Negatives:", fn)
print("True Positives :", tp)

attack_recall = tp / (tp + fn)

false_positive_rate = fp / (fp + tn)

print(
    f"\nAttack Detection Rate (Recall): "
    f"{attack_recall * 100:.2f}%"
)

print(
    f"False Positive Rate: "
    f"{false_positive_rate * 100:.2f}%"
)

print("\n======================================")
print("ANOMALY V3 EVALUATION COMPLETED!")
print("======================================")