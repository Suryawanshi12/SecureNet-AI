import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix
)


# ============================================================
# 1. LOAD TRAINED MODEL
# ============================================================

print("Loading trained model...")

model = joblib.load(
    "models/xgboost_ids_model.pkl"
)

print("Model loaded successfully!")


# ============================================================
# 2. LOAD TEST DATA
# ============================================================

print("\nLoading test data...")

df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 3. SEPARATE FEATURES AND LABEL
# ============================================================

X_test = df.drop(
    columns=["Label"]
)

y_test = df["Label"]


# ============================================================
# 4. MAKE PREDICTIONS
# ============================================================

print("\nMaking predictions...")

y_pred = model.predict(X_test)

print("Prediction completed!")


# ============================================================
# 5. ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n======================================")
print("MODEL EVALUATION")
print("======================================")

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ============================================================
# 6. CLASS NAMES
# ============================================================

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


# ============================================================
# 7. CLASSIFICATION REPORT
# ============================================================

print("\n======================================")
print("CLASSIFICATION REPORT")
print("======================================")

print(
    classification_report(
        y_test,
        y_pred,
        labels=list(range(15)),
        target_names=class_names,
        zero_division=0
    )
)


# ============================================================
# 8. CONFUSION MATRIX
# ============================================================

print("\nCreating confusion matrix...")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=list(range(15))
)


# ============================================================
# 9. DISPLAY CONFUSION MATRIX
# ============================================================

plt.figure(figsize=(18, 15))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_names,
    yticklabels=class_names
)

plt.title(
    "SecureNet AI - XGBoost Confusion Matrix",
    fontsize=18
)

plt.xlabel(
    "Predicted Label",
    fontsize=13
)

plt.ylabel(
    "Actual Label",
    fontsize=13
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.yticks(
    rotation=0
)

plt.tight_layout()


# ============================================================
# 10. SAVE CONFUSION MATRIX
# ============================================================

output_file = "reports/confusion_matrix.png"

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

print("\nConfusion matrix saved to:")
print(output_file)


# ============================================================
# 11. SHOW CONFUSION MATRIX
# ============================================================

plt.show()


print("\n======================================")
print("EVALUATION COMPLETED!")
print("======================================")