import pandas as pd
import numpy as np
import joblib
import shap


# ==========================================
# SECURENET AI - UNIFIED PREDICTION PIPELINE
# ==========================================

print("Loading models...")

# XGBoost Model 5
xgb_model = joblib.load(
    "models/xgboost_ids_model_v5.pkl"
)

# Isolation Forest V3
anomaly_model = joblib.load(
    "models/isolation_forest_model_v3.pkl"
)

print("Models loaded successfully!")


# ==========================================
# SHAP EXPLAINER
# ==========================================

print("Loading SHAP explainer...")

explainer = shap.TreeExplainer(xgb_model)

print("SHAP explainer loaded!")


# ==========================================
# CLASS NAMES
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
# ATTACK SEVERITY
# ==========================================

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


# ==========================================
# ANOMALY SETTINGS
# ==========================================

THRESHOLD = -0.145540

MIN_SCORE = -0.26661372175449094


# ==========================================
# RISK LEVEL
# ==========================================

def get_risk_level(score):

    if score <= 25:
        return "LOW"

    elif score <= 50:
        return "MEDIUM"

    elif score <= 75:
        return "HIGH"

    else:
        return "CRITICAL"


# ==========================================
# SHAP EXPLANATION
# ==========================================

def get_shap_explanation(X, predicted_class, top_n=10):

    """
    Returns the top features responsible for
    the predicted class.
    """

    shap_values = explainer.shap_values(X)

    # SHAP for multiclass XGBoost normally has:
    # samples × features × classes

    if isinstance(shap_values, list):

        sample_shap = shap_values[
            predicted_class
        ][0]

    else:

        shap_array = np.asarray(shap_values)

        if shap_array.ndim == 3:

            sample_shap = shap_array[
                0, :, predicted_class
            ]

        elif shap_array.ndim == 2:

            sample_shap = shap_array[0]

        else:

            raise ValueError(
                f"Unexpected SHAP shape: {shap_array.shape}"
            )

    feature_names = X.columns

    feature_values = X.iloc[0].values

    # Rank by absolute SHAP value
    top_indices = np.argsort(
        np.abs(sample_shap)
    )[::-1][:top_n]

    explanations = []

    for index in top_indices:

        shap_value = float(
            sample_shap[index]
        )

        feature_name = feature_names[index]

        feature_value = feature_values[index]

        if shap_value > 0:

            direction = "increased"

        else:

            direction = "decreased"

        explanations.append({
            "feature": feature_name,
            "value": float(feature_value),
            "shap_value": round(
                shap_value, 6
            ),
            "direction": direction
        })

    return explanations


# ==========================================
# PREDICTION FUNCTION
# ==========================================

def predict_flow(flow_data):

    """
    Takes one network-flow record and returns:

    - Prediction
    - Confidence
    - Attack severity
    - Anomaly score
    - Risk score
    - Risk level
    - SHAP explanation
    """

    # --------------------------------------
    # Convert input into DataFrame
    # --------------------------------------

    X = pd.DataFrame([flow_data])

    # --------------------------------------
    # XGBoost Prediction
    # --------------------------------------

    predicted_class = int(
        xgb_model.predict(X)[0]
    )

    probabilities = xgb_model.predict_proba(X)[0]

    confidence = float(
        probabilities.max() * 100
    )

    predicted_label = class_names[
        predicted_class
    ]

    # --------------------------------------
    # Anomaly Detection
    # --------------------------------------

    raw_anomaly_score = float(
        anomaly_model.decision_function(X)[0]
    )

    if raw_anomaly_score >= THRESHOLD:

        anomaly_score = 0.0

    else:

        anomaly_score = (
            (THRESHOLD - raw_anomaly_score)
            /
            (THRESHOLD - MIN_SCORE)
        ) * 100

        anomaly_score = float(
            np.clip(
                anomaly_score,
                0,
                100
            )
        )

    # --------------------------------------
    # Attack Severity
    # --------------------------------------

    severity = attack_severity[
        predicted_label
    ]

    # --------------------------------------
    # Risk Score
    # --------------------------------------

    if predicted_label == "BENIGN":

        confidence_uncertainty = (
            100 - confidence
        )

        risk_score = (
            0.30 * confidence_uncertainty
            +
            0.70 * anomaly_score
        )

    else:

        risk_score = (
            0.50 * severity
            +
            0.30 * confidence
            +
            0.20 * anomaly_score
        )

    risk_score = float(
        np.clip(
            risk_score,
            0,
            100
        )
    )

    # --------------------------------------
    # Risk Level
    # --------------------------------------

    risk_level = get_risk_level(
        risk_score
    )

    # --------------------------------------
    # SHAP Explanation
    # --------------------------------------

    shap_explanation = get_shap_explanation(
        X,
        predicted_class,
        top_n=10
    )

    # --------------------------------------
    # Final Result
    # --------------------------------------

    result = {

        "prediction": predicted_label,

        "confidence": round(
            confidence,
            2
        ),

        "attack_severity": severity,

        "anomaly_score": round(
            anomaly_score,
            2
        ),

        "risk_score": round(
            risk_score,
            2
        ),

        "risk_level": risk_level,

        "explanation": shap_explanation
    }

    return result


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("\n======================================")
    print("TESTING SECURENET AI PIPELINE")
    print("======================================")

    # --------------------------------------
    # Load test data
    # --------------------------------------

    print("\nLoading test data...")

    test_df = pd.read_csv(
        "data/processed/test_encoded.csv",
        low_memory=False
    )

    print("Test data loaded!")
    print(
        "Total rows:",
        len(test_df)
    )

    # --------------------------------------
    # Select known DDoS sample
    # --------------------------------------

    print(
        "\nSelecting a known DDoS sample..."
    )

    attack_row = test_df[
        test_df["Label"] == 2
    ].iloc[0]

    print("Actual class: DDoS")

    # --------------------------------------
    # Remove Label
    # --------------------------------------

    test_flow = attack_row.drop(
        labels=["Label"]
    ).to_dict()

    # --------------------------------------
    # Run prediction
    # --------------------------------------

    result = predict_flow(
        test_flow
    )

    # --------------------------------------
    # Display prediction
    # --------------------------------------

    print("\n======================================")
    print("PREDICTION RESULT")
    print("======================================")

    print(
        "Prediction:",
        result["prediction"]
    )

    print(
        "Confidence:",
        result["confidence"],
        "%"
    )

    print(
        "Attack Severity:",
        result["attack_severity"]
    )

    print(
        "Anomaly Score:",
        result["anomaly_score"]
    )

    print(
        "Risk Score:",
        result["risk_score"]
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )

    # --------------------------------------
    # Display SHAP explanation
    # --------------------------------------

    print("\n======================================")
    print("TOP SHAP FEATURES")
    print("======================================")

    for i, item in enumerate(
        result["explanation"],
        start=1
    ):

        print(
            f"{i}. "
            f"{item['feature']} | "
            f"Value: {item['value']} | "
            f"SHAP: {item['shap_value']} | "
            f"{item['direction']}"
        )

    print("\n======================================")
    print("PIPELINE TEST COMPLETED")
    print("======================================")