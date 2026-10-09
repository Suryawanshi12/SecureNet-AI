import pandas as pd

input_file = "data/processed/train_encoded.csv"
output_file = "data/processed/train_balanced.csv"

print("Loading training data...")

df = pd.read_csv(input_file, low_memory=False)

print("Training data loaded!")
print("Total rows:", len(df))


# Maximum number of samples per class
MAX_SAMPLES = {
    0: 100000,   # BENIGN
    1: 5000,     # Bot
    2: 20000,    # DDoS
    3: 5000,     # DoS GoldenEye
    4: 20000,    # DoS Hulk
    5: 5000,     # FTP-Patator
    6: 5000,     # DoS slowloris
    7: 5000,     # DoS Slowhttptest
    8: 5000,     # Heartbleed
    9: 5000,     # Infiltration
    10: 20000,   # PortScan
    11: 5000,    # SSH-Patator
    12: 5000,    # Web Attack - Brute Force
    13: 5000,    # Web Attack - Sql Injection
    14: 5000     # Web Attack - XSS
}


samples = []

print("\nCreating balanced training dataset...")

for label, max_samples in MAX_SAMPLES.items():

    class_data = df[df["Label"] == label]

    # If class has fewer rows than maximum,
    # keep all available rows.
    n = min(len(class_data), max_samples)

    sampled = class_data.sample(
        n=n,
        random_state=42
    )

    samples.append(sampled)

    print(
        f"Class {label}: "
        f"available={len(class_data)}, "
        f"selected={n}"
    )


# Combine all classes
balanced_df = pd.concat(samples)

# Shuffle final dataset
balanced_df = balanced_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# Save
balanced_df.to_csv(
    output_file,
    index=False
)

print("\n================================")
print("Balanced dataset created!")
print("================================")

print("Rows:", len(balanced_df))
print("Columns:", len(balanced_df.columns))

print("\nClass distribution:")
print(balanced_df["Label"].value_counts().sort_index())

print("\nSaved to:")
print(output_file)