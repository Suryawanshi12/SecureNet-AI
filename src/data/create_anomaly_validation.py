import pandas as pd
from sklearn.model_selection import train_test_split

print("Loading training data...")

df = pd.read_csv(
    "data/processed/train_encoded.csv",
    low_memory=False
)

print("Training data loaded!")
print("Total rows:", len(df))

# Keep only BENIGN traffic
benign_df = df[df["Label"] == 0].copy()

print("\nTotal BENIGN samples:", len(benign_df))

# Split BENIGN data into:
# 90% -> anomaly detector training
# 10% -> validation for threshold selection

benign_train, benign_validation = train_test_split(
    benign_df,
    test_size=0.10,
    random_state=42
)

print("\nBENIGN training samples:", len(benign_train))
print("BENIGN validation samples:", len(benign_validation))

# Save files
benign_train.to_csv(
    "data/processed/anomaly_train_benign.csv",
    index=False
)

benign_validation.to_csv(
    "data/processed/anomaly_validation_benign.csv",
    index=False
)

print("\nFiles saved:")
print("1. data/processed/anomaly_train_benign.csv")
print("2. data/processed/anomaly_validation_benign.csv")

print("\n======================================")
print("ANOMALY VALIDATION DATA CREATED!")
print("======================================")