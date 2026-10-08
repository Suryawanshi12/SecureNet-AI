import pandas as pd
import joblib

# ==========================================
# 1. Load Model and Test Data
# ==========================================

print("Loading model...")

model = joblib.load("models/xgboost_ids_model.pkl")

print("Model loaded!")

print("\nLoading test data...")

df = pd.read_csv(
    "data/processed/test_encoded.csv",
    low_memory=False
)

print("Test data loaded!")
print("Rows:", len(df))


# ==========================================
# 2. Separate Features and Target
# ==========================================

X = df.drop(columns=["Label"])
y = df["Label"]

print("\nMaking predictions...")

y_pred = model.predict(X)

print("Predictions completed!")


# ==========================================
# 3. XSS Label = 14
#    Brute Force Label = 12
# ==========================================

XSS = 14
BRUTE_FORCE = 12
BENIGN = 0


# ==========================================
# 4. Create Three Groups
# ==========================================

# Correctly predicted XSS
correct_xss = (y == XSS) & (y_pred == XSS)

# XSS predicted as Brute Force
xss_as_bruteforce = (y == XSS) & (y_pred == BRUTE_FORCE)

# XSS predicted as BENIGN
xss_as_benign = (y == XSS) & (y_pred == BENIGN)


print("\n======================================")
print("XSS FEATURE ANALYSIS")
print("======================================")

print("\nCorrect XSS samples:", correct_xss.sum())
print("XSS → Brute Force:", xss_as_bruteforce.sum())
print("XSS → BENIGN:", xss_as_benign.sum())


# ==========================================
# 5. Select Feature Columns
# ==========================================

feature_columns = X.columns


# ==========================================
# 6. Calculate Mean Feature Values
# ==========================================

correct_mean = X.loc[correct_xss, feature_columns].mean()

bruteforce_mean = X.loc[
    xss_as_bruteforce,
    feature_columns
].mean()

benign_mean = X.loc[
    xss_as_benign,
    feature_columns
].mean()


# ==========================================
# 7. Create Comparison Table
# ==========================================

comparison = pd.DataFrame({
    "Feature": feature_columns,
    "Correct_XSS_Mean": correct_mean.values,
    "XSS_as_BruteForce_Mean": bruteforce_mean.values,
    "XSS_as_BENIGN_Mean": benign_mean.values
})


# ==========================================
# 8. Calculate Difference
# ==========================================

comparison["Difference_XSS_vs_BruteForce"] = (
    comparison["Correct_XSS_Mean"]
    - comparison["XSS_as_BruteForce_Mean"]
).abs()


# ==========================================
# 9. Sort Most Different Features
# ==========================================

comparison = comparison.sort_values(
    "Difference_XSS_vs_BruteForce",
    ascending=False
)


# ==========================================
# 10. Display Top 20 Features
# ==========================================

print("\nTop 20 features showing difference")
print("between Correct XSS and XSS → Brute Force:\n")

print(
    comparison.head(20).to_string(index=False)
)


# ==========================================
# 11. Save Results
# ==========================================

output_path = "reports/xss_feature_analysis.csv"

comparison.to_csv(
    output_path,
    index=False
)

print("\nFeature analysis saved to:")
print(output_path)


print("\n======================================")
print("FEATURE ANALYSIS COMPLETED!")
print("======================================")