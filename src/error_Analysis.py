import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix

# ==========================================
# 1. Load Model
# ==========================================

print("Loading model...")

model = joblib.load("models/xgboost_ids_model.pkl")

print("Model loaded!")


# ==========================================
# 2. Load Test Dataset
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
# 4. Predict
# ==========================================

print("\nMaking predictions...")

y_pred = model.predict(X_test)

print("Predictions completed!")


# ==========================================
# 5. Class Names
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


# ==========================================
# 6. Find Misclassified Samples
# ==========================================

print("\nFinding misclassified samples...")

misclassified = df[y_test != y_pred].copy()

misclassified["Actual_Label"] = y_test[y_test != y_pred]
misclassified["Predicted_Label"] = y_pred[y_test != y_pred]

misclassified["Actual_Class"] = misclassified["Actual_Label"].map(
    dict(enumerate(class_names))
)

misclassified["Predicted_Class"] = misclassified["Predicted_Label"].map(
    dict(enumerate(class_names))
)


# ==========================================
# 7. Print Total Errors
# ==========================================

print("\n======================================")
print("ERROR ANALYSIS")
print("======================================")

print("\nTotal test samples:", len(df))
print("Total misclassified:", len(misclassified))


# ==========================================
# 8. Misclassification Summary
# ==========================================

print("\nMisclassification Summary:")

summary = (
    misclassified
    .groupby(["Actual_Class", "Predicted_Class"])
    .size()
    .reset_index(name="Count")
    .sort_values("Count", ascending=False)
)

print(summary.to_string(index=False))


# ==========================================
# 9. XSS Error Analysis
# ==========================================

print("\n======================================")
print("XSS ERROR ANALYSIS")
print("======================================")

xss_errors = misclassified[
    misclassified["Actual_Class"] == "Web Attack - XSS"
]

if len(xss_errors) > 0:

    xss_summary = (
        xss_errors["Predicted_Class"]
        .value_counts()
        .reset_index()
    )

    xss_summary.columns = [
        "Predicted_As",
        "Count"
    ]

    print("\nActual XSS samples incorrectly classified as:")

    print(xss_summary.to_string(index=False))

else:

    print("No XSS misclassifications found.")


# ==========================================
# 10. Save All Errors
# ==========================================

output_path = "reports/misclassified_samples.csv"

misclassified.to_csv(
    output_path,
    index=False
)

print("\nMisclassified samples saved to:")
print(output_path)


# ==========================================
# 11. Save Summary
# ==========================================

summary_path = "reports/misclassification_summary.csv"

summary.to_csv(
    summary_path,
    index=False
)

print("\nMisclassification summary saved to:")
print(summary_path)


print("\n======================================")
print("ERROR ANALYSIS COMPLETED!")
print("======================================")