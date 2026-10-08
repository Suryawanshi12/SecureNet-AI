import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

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
# 6. Confusion Matrix
# ==========================================

print("\nCreating confusion matrix...")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=list(range(15))
)


# ==========================================
# 7. Display Confusion Matrix
# ==========================================

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
    "SecureNet AI - XGBoost Model 4 Confusion Matrix",
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

plt.yticks(rotation=0)

plt.tight_layout()


# ==========================================
# 8. Save Figure
# ==========================================

output_path = "reports/confusion_matrix_v4.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print("\nConfusion matrix saved to:")
print(output_path)

plt.show()


print("\n======================================")
print("MODEL 4 CONFUSION MATRIX COMPLETED!")
print("======================================")