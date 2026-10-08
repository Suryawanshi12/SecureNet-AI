import pandas as pd

from src.predict import predict_flow


# ============================================================
# SECURENET AI
# API FEATURE VALIDATION
# ============================================================

# These are the feature names expected by the TRAINED XGBOOST
# MODEL.

EXPECTED_MODEL_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Max",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Fwd Packet Length Std",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Fwd IAT Mean",
    "Fwd IAT Std",
    "Fwd IAT Max",
    "Fwd IAT Min",
    "Bwd IAT Total",
    "Bwd IAT Mean",
    "Bwd IAT Std",
    "Bwd IAT Max",
    "Bwd IAT Min",
    "Fwd PSH Flags",
    "Bwd PSH Flags",
    "Fwd URG Flags",
    "Bwd URG Flags",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "CWE Flag Count",
    "ECE Flag Count",
    "Down/Up Ratio",
    "Average Packet Size",
    "Avg Fwd Segment Size",
    "Avg Bwd Segment Size",
    "Fwd Header Length.1",
    "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk",
    "Fwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate",
    "Subflow Fwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Bwd Packets",
    "Subflow Bwd Bytes",
    "Init_Win_bytes_forward",
    "Init_Win_bytes_backward",
    "act_data_pkt_fwd",
    "min_seg_size_forward",
    "Active Mean",
    "Active Std",
    "Active Max",
    "Active Min",
    "Idle Mean",
    "Idle Std",
    "Idle Max",
    "Idle Min",
]


# ============================================================
# DATASET → MODEL FEATURE NAME MAPPING
# ============================================================

FEATURE_NAME_MAPPING = {
    "FwdIAT Max": "Fwd IAT Max",
    "Fwd AvgBulk Rate": "Fwd Avg Bulk Rate",
}


# ============================================================
# NORMALIZE FEATURE NAMES
# ============================================================

def normalize_features(features: dict):
    """
    Convert incoming dataset/API feature names into the exact
    feature names expected by the trained ML model.
    """

    normalized = {}

    for key, value in features.items():

        # Remove accidental leading/trailing spaces
        clean_key = key.strip()

        # Convert dataset name → model name
        clean_key = FEATURE_NAME_MAPPING.get(
            clean_key,
            clean_key
        )

        normalized[clean_key] = value

    return normalized


# ============================================================
# VALIDATE FEATURES
# ============================================================

def validate_features(features: dict):

    features = normalize_features(features)

    expected = set(EXPECTED_MODEL_FEATURES)
    received = set(features.keys())

    # --------------------------------------------------------
    # Missing features
    # --------------------------------------------------------

    missing_features = expected - received

    if missing_features:
        raise ValueError(
            f"Missing required features: "
            f"{sorted(missing_features)}"
        )

    # --------------------------------------------------------
    # Extra features
    # --------------------------------------------------------

    extra_features = received - expected

    if extra_features:
        raise ValueError(
            f"Unexpected features received: "
            f"{sorted(extra_features)}"
        )

    # --------------------------------------------------------
    # Feature count
    # --------------------------------------------------------

    if len(features) != len(EXPECTED_MODEL_FEATURES):
        raise ValueError(
            f"Expected {len(EXPECTED_MODEL_FEATURES)} features, "
            f"but received {len(features)} features."
        )

    return features


# ============================================================
# ANALYZE NETWORK FLOW
# ============================================================

def analyze_network_flow(features: dict):

    # --------------------------------------------------------
    # STEP 1
    # Normalize + validate
    # --------------------------------------------------------

    features = validate_features(features)

    # --------------------------------------------------------
    # STEP 2
    # Put features in exact model order
    # --------------------------------------------------------

    ordered_features = {
        feature: features[feature]
        for feature in EXPECTED_MODEL_FEATURES
    }

    # --------------------------------------------------------
    # STEP 3
    # Create DataFrame
    # --------------------------------------------------------

    flow_df = pd.DataFrame(
        [ordered_features],
        columns=EXPECTED_MODEL_FEATURES
    )

    # --------------------------------------------------------
    # STEP 4
    # Convert values to numeric
    # --------------------------------------------------------

    for column in flow_df.columns:

        flow_df[column] = pd.to_numeric(
            flow_df[column],
            errors="raise"
        )

    # --------------------------------------------------------
    # STEP 5
    # Convert to dictionary
    # --------------------------------------------------------

    flow_data = flow_df.iloc[0].to_dict()

    # --------------------------------------------------------
    # STEP 6
    # Run complete ML pipeline
    # --------------------------------------------------------

    result = predict_flow(flow_data)

    # --------------------------------------------------------
    # STEP 7
    # Return result
    # --------------------------------------------------------

    return result