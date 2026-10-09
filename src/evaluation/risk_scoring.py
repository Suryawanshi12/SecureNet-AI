import pandas as pd
import numpy as np
import joblib

print("======================================")
print("SECURENET AI - RISK SCORING V2")
print("======================================")


# ============================================================
# 1. LOAD MODELS
# ============================================================

print("\nLoading XGBoost Model 5...")

xgb_model = joblib.load(
    "models/xgboost_ids_model_v5.pkl"
)

print("XGBoost Model 5 loaded!")


print("\nLoading Isolation Forest V3...")

anomaly_model = joblib.load(
    "models/isolation_forest_model_v3.pkl"
)

print("Isolation Forest V3 loaded!")


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


X = df.drop(columns=["Label"])
y_actual = df["Label"]


# ============================================================
# 3. CLASS NAMES
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
# 4. ATTACK SEVERITY
# ============================================================

attack_severity = {
    "BENIGN": 0,

    "Bot": 50,
    "PortScan": 55,

    "FTP-Patator": 65,
    "SSH-Patator": 65,

    "Web Attack - Brute Force": 70,
    "Web Attack - XSS": 70,

    "Web Attack - Sql Injection": 80,

    "DoS slowloris": 85,
    "DoS Slowhttptest": 85,
    "DoS GoldenEye": 85,
    "DoS Hulk": 85,

    "DDoS": 95,
    "Infiltration": 95,

    "Heartbleed": 100
}


# ============================================================
# 5. XGBOOST PREDICTION
# ============================================================

print("\nRunning XGBoost predictions...")

predicted_classes = xgb_model.predict(X)

predicted_probabilities = xgb_model.predict_proba(X)

print("XGBoost predictions completed!")


# ============================================================
# 6. XGBOOST CONFIDENCE
# ============================================================

xgb_confidence = predicted_probabilities.max(axis=1)

# Convert 0-1 → 0-100
xgb_confidence_score = xgb_confidence * 100


# ============================================================
# 7. ISOLATION FOREST RAW SCORE
# ============================================================

print("\nCalculating anomaly scores...")

raw_anomaly_scores = anomaly_model.decision_function(X)

print("Anomaly scores calculated!")


# ============================================================
# 8. ANOMALY SCORE NORMALIZATION
# ============================================================

# Threshold selected using BENIGN validation data
THRESHOLD = -0.145540

# Minimum score observed in the test set
MIN_SCORE = raw_anomaly_scores.min()

# For scores ABOVE threshold:
# traffic is considered normal → anomaly score = 0
#
# For scores BELOW threshold:
# lower score → more anomalous

anomaly_score = np.where(
    raw_anomaly_scores >= THRESHOLD,
    0,
    (
        (THRESHOLD - raw_anomaly_scores)
        /
        (THRESHOLD - MIN_SCORE)
    ) * 100
)

# Keep between 0 and 100
anomaly_score = np.clip(
    anomaly_score,
    0,
    100
)


# ============================================================
# 9. CONVERT PREDICTIONS TO CLASS NAMES
# ============================================================

predicted_labels = [
    class_names[int(class_id)]
    for class_id in predicted_classes
]


# ============================================================
# 10. ATTACK SEVERITY
# ============================================================

severity_score = np.array([
    attack_severity[label]
    for label in predicted_labels
])


# ============================================================
# 11. FINAL RISK SCORE
# ============================================================

risk_score = np.zeros(len(df))


for i in range(len(df)):

    prediction = predicted_labels[i]

    confidence = xgb_confidence_score[i]

    anomaly = anomaly_score[i]

    severity = severity_score[i]


    # --------------------------------------------------------
    # CASE 1: BENIGN prediction
    # --------------------------------------------------------

    if prediction == "BENIGN":

        # High confidence in BENIGN should LOWER risk.
        #
        # Only uncertainty + anomaly should contribute.

        confidence_uncertainty = 100 - confidence

        risk = (
            0.30 * confidence_uncertainty
            +
            0.70 * anomaly
        )


    # --------------------------------------------------------
    # CASE 2: Known attack prediction
    # --------------------------------------------------------

    else:

        risk = (
            0.50 * severity
            +
            0.30 * confidence
            +
            0.20 * anomaly
        )


    risk_score[i] = risk


# Keep risk between 0 and 100
risk_score = np.clip(
    risk_score,
    0,
    100
)


# ============================================================
# 12. RISK LEVEL
# ============================================================

def get_risk_level(score):

    if score <= 25:
        return "LOW"

    elif score <= 50:
        return "MEDIUM"

    elif score <= 75:
        return "HIGH"

    else:
        return "CRITICAL"


risk_levels = [
    get_risk_level(score)
    for score in risk_score
]


# ============================================================
# 13. CREATE RESULTS DATAFRAME
# ============================================================

results = pd.DataFrame({

    "Actual_Label": [
        class_names[int(label)]
        for label in y_actual
    ],

    "Predicted_Attack": predicted_labels,

    "XGBoost_Confidence": np.round(
        xgb_confidence_score,
        2
    ),

    "Attack_Severity": severity_score,

    "Anomaly_Raw_Score": np.round(
        raw_anomaly_scores,
        6
    ),

    "Anomaly_Score": np.round(
        anomaly_score,
        2
    ),

    "Risk_Score": np.round(
        risk_score,
        2
    ),

    "Risk_Level": risk_levels
})


# ============================================================
# 14. DISPLAY FIRST 20 RESULTS
# ============================================================

print("\n======================================")
print("RISK SCORING RESULTS")
print("======================================")

print(
    results.head(20).to_string(index=False)
)


# ============================================================
# 15. RISK LEVEL DISTRIBUTION
# ============================================================

print("\n======================================")
print("RISK LEVEL DISTRIBUTION")
print("======================================")

print(
    results["Risk_Level"].value_counts()
)


# ============================================================
# 16. PREDICTED ATTACK DISTRIBUTION
# ============================================================

print("\n======================================")
print("PREDICTED ATTACK DISTRIBUTION")
print("======================================")

print(
    results["Predicted_Attack"].value_counts()
)


# ============================================================
# 17. AVERAGE RISK BY PREDICTED CLASS
# ============================================================

print("\n======================================")
print("AVERAGE RISK BY PREDICTED ATTACK")
print("======================================")

average_risk = (
    results
    .groupby("Predicted_Attack")["Risk_Score"]
    .mean()
    .sort_values(ascending=False)
)

print(average_risk)


# ============================================================
# 18. SAVE RESULTS
# ============================================================

output_path = (
    "reports/risk_scoring_results_v2.csv"
)

results.to_csv(
    output_path,
    index=False
)

print("\nResults saved to:")
print(output_path)


print("\n======================================")
print("RISK SCORING V2 COMPLETED!")
print("======================================")