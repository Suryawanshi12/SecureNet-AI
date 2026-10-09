import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

train_file = "data/processed/train.csv"
test_file = "data/processed/test.csv"

train = pd.read_csv(train_file, low_memory=False)
test = pd.read_csv(test_file, low_memory=False)

# Create encoder
encoder = LabelEncoder()

# Learn class mapping from training data
train["Label"] = encoder.fit_transform(train["Label"])

# Apply the SAME mapping to test data
test["Label"] = encoder.transform(test["Label"])

# Save encoded datasets
train.to_csv("data/processed/train_encoded.csv", index=False)
test.to_csv("data/processed/test_encoded.csv", index=False)

# Save encoder for later predictions
joblib.dump(encoder, "models/label_encoder.pkl")

print("Label encoding completed!")

print("\nClass Mapping:")
for number, label in enumerate(encoder.classes_):
    print(f"{number} -> {label}")

print("\nFiles created:")
print("train_encoded.csv")
print("test_encoded.csv")
print("label_encoder.pkl")