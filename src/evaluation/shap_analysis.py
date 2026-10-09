import pandas as pd
import joblib
import shap
import numpy as np

print("Loading Model 5...")
model = joblib.load("models/xgboost_ids_model_v5.pkl")
print("Model 5 loaded!")

print("\nLoading test data...")
df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")

X_test = df.drop(columns=["Label"])
y_test = df["Label"]

# Take a small sample
X_sample = X_test.sample(
    n=1000,
    random_state=42
)

y_sample = y_test.loc[X_sample.index]

print("\nCreating SHAP explainer...")
explainer = shap.TreeExplainer(model)

print("Calculating SHAP values...")
shap_values = explainer.shap_values(X_sample)

print("SHAP calculation completed!")

# --------------------------------------------------
# Class names
# --------------------------------------------------

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

# --------------------------------------------------
# Predictions
# --------------------------------------------------

predictions = model.predict(X_sample)

print("\n======================================")
print("SHAP EXPLANATION")
print("======================================")

# Explain first 5 samples
for i in range(5):

    actual_class = int(y_sample.iloc[i])
    predicted_class = int(predictions[i])

    print("\n--------------------------------------")
    print(f"Sample {i + 1}")
    print("--------------------------------------")

    print("Actual Label    :", class_names[actual_class])
    print("Predicted Label :", class_names[predicted_class])

    # SHAP values for predicted class
    sample_shap = shap_values[i, :, predicted_class]

    # Get feature importance
    feature_importance = np.abs(sample_shap)

    # Top 10 features
    top_indices = np.argsort(feature_importance)[::-1][:10]

    print("\nTop contributing features:")

    for rank, feature_index in enumerate(top_indices, start=1):

        feature_name = X_sample.columns[feature_index]
        shap_value = sample_shap[feature_index]
        feature_value = X_sample.iloc[i, feature_index]

        direction = "increased" if shap_value > 0 else "decreased"

        print(
            f"{rank}. {feature_name}"
            f" | Value: {feature_value:.4f}"
            f" | SHAP: {shap_value:.4f}"
            f" | {direction} prediction"
        )

print("\n======================================")
print("SHAP EXPLANATION COMPLETED!")
print("======================================")