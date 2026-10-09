import pandas as pd
import joblib
import numpy as np

print("Loading Isolation Forest V3...")

model = joblib.load(
    "models/isolation_forest_model_v3.pkl"
)

print("Model loaded!")

print("\nLoading BENIGN validation data...")

df = pd.read_csv(
    "data/processed/anomaly_validation_benign.csv",
    low_memory=False
)

print("Validation data loaded!")
print("Rows:", len(df))

X = df.drop(columns=["Label"])

print("\nCalculating anomaly scores...")

# Higher score = more normal
# Lower score = more anomalous
scores = model.decision_function(X)

print("Scores calculated!")

print("\n======================================")
print("ANOMALY SCORE ANALYSIS")
print("======================================")

print("\nMinimum score:", scores.min())
print("Maximum score:", scores.max())
print("Mean score   :", scores.mean())
print("Median score :", np.median(scores))

print("\nScore percentiles:")

for percentile in [0.1, 0.5, 1, 2, 5, 10]:
    value = np.percentile(scores, percentile)

    print(
        f"{percentile}% percentile : {value:.6f}"
    )

print("\n======================================")
print("THRESHOLD ANALYSIS")
print("======================================")

# Test several possible thresholds
thresholds = [
    np.percentile(scores, 0.1),
    np.percentile(scores, 0.5),
    np.percentile(scores, 1),
    np.percentile(scores, 2),
    np.percentile(scores, 5)
]

for threshold in thresholds:

    anomaly_count = (scores < threshold).sum()

    false_positive_rate = (
        anomaly_count / len(scores)
    ) * 100

    print(
        f"\nThreshold: {threshold:.6f}"
    )

    print(
        f"Normal traffic marked as anomaly: "
        f"{anomaly_count}"
    )

    print(
        f"False Positive Rate: "
        f"{false_positive_rate:.2f}%"
    )

print("\n======================================")
print("THRESHOLD ANALYSIS COMPLETED!")
print("======================================")