import pandas as pd
import joblib

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

errors = y_test != y_pred

misclassified = df.loc[errors].copy()

misclassified["Actual_Label"] = y_test[errors]
misclassified["Predicted_Label"] = y_pred[errors]

misclassified["Actual_Class"] = (
    misclassified["Actual_Label"]
    .map(dict(enumerate(class_names)))
)

misclassified["Predicted_Class"] = (
    misclassified["Predicted_Label"]
    .map(dict(enumerate(class_names)))
)


# ==========================================
# 7. Overall Error Analysis
# ==========================================

print("\n======================================")
print("MODEL 4 ERROR ANALYSIS")
print("======================================")

print("\nTotal test samples:", len(df))
print("Total misclassified:", len(misclassified))


# ==========================================
# 8. Misclassification Summary
# ==========================================

summary = (
    misclassified
    .groupby(["Actual_Class", "Predicted_Class"])
    .size()
    .reset_index(name="Count")
    .sort_values("Count", ascending=False)
)

print("\nMisclassification Summary:\n")

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

    print("\nActual XSS incorrectly classified as:")

    xss_summary = (
        xss_errors["Predicted_Class"]
        .value_counts()
        .reset_index()
    )

    xss_summary.columns = [
        "Predicted_As",
        "Count"
    ]

    print(xss_summary.to_string(index=False))

else:
    print("No XSS errors found.")


# ==========================================
# 10. Brute Force Error Analysis
# ==========================================

print("\n======================================")
print("BRUTE FORCE ERROR ANALYSIS")
print("======================================")

brute_errors = misclassified[
    misclassified["Actual_Class"] == "Web Attack - Brute Force"
]

if len(brute_errors) > 0:

    print("\nActual Brute Force incorrectly classified as:")

    brute_summary = (
        brute_errors["Predicted_Class"]
        .value_counts()
        .reset_index()
    )

    brute_summary.columns = [
        "Predicted_As",
        "Count"
    ]

    print(brute_summary.to_string(index=False))

else:
    print("No Brute Force errors found.")


# ==========================================
# 11. XSS <-> Brute Force Confusion
# ==========================================

print("\n======================================")
print("XSS <-> BRUTE FORCE CONFUSION")
print("======================================")

xss_to_brute = len(
    misclassified[
        (misclassified["Actual_Class"] == "Web Attack - XSS") &
        (misclassified["Predicted_Class"] == "Web Attack - Brute Force")
    ]
)

brute_to_xss = len(
    misclassified[
        (misclassified["Actual_Class"] == "Web Attack - Brute Force") &
        (misclassified["Predicted_Class"] == "Web Attack - XSS")
    ]
)

print("\nXSS -> Brute Force:", xss_to_brute)
print("Brute Force -> XSS:", brute_to_xss)


# ==========================================
# 12. Save All Misclassified Samples
# ==========================================

output_path = "reports/misclassified_samples_v4.csv"

misclassified.to_csv(
    output_path,
    index=False
)

print("\nMisclassified samples saved to:")
print(output_path)


# ==========================================
# 13. Save Summary
# ==========================================

summary_path = "reports/misclassification_summary_v4.csv"

summary.to_csv(
    summary_path,
    index=False
)

print("\nMisclassification summary saved to:")
print(summary_path)


print("\n======================================")
print("MODEL 4 ERROR ANALYSIS COMPLETED!")
print("======================================")