import pandas as pd

input_file = "data/processed/train_encoded.csv"
output_file = "data/processed/train_sample.csv"

# Read encoded training data
df = pd.read_csv(input_file, low_memory=False)

# Take 200,000 rows randomly
sample = df.sample(
    n=200000,
    random_state=42
)

sample.to_csv(output_file, index=False)

print("Training sample created!")
print("Rows:", len(sample))
print("Columns:", len(sample.columns))

print("\nClass distribution:")
print(sample["Label"].value_counts())