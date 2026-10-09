import pandas as pd
from sklearn.model_selection import train_test_split

input_file = "data/processed/master_dataset_clean.csv"

train_file = "data/processed/train.csv"
test_file = "data/processed/test.csv"

# --------------------------------------------------
# Step 1: Read only the Label column
# --------------------------------------------------

print("Reading labels...")

labels = pd.read_csv(
    input_file,
    usecols=["Label"]
)

# Create row numbers
indices = labels.index

# --------------------------------------------------
# Step 2: Stratified Train-Test Split
# --------------------------------------------------

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=labels["Label"]
)

train_indices = set(train_indices)
test_indices = set(test_indices)

print("Train rows:", len(train_indices))
print("Test rows:", len(test_indices))

# --------------------------------------------------
# Step 3: Read complete dataset in chunks
# --------------------------------------------------

print("Creating train.csv and test.csv...")

first_chunk = True

for chunk in pd.read_csv(input_file, chunksize=100000):

    # Get original row numbers of this chunk
    start = chunk.index[0]
    end = chunk.index[-1] + 1

    chunk_indices = range(start, end)

    train_mask = [i in train_indices for i in chunk_indices]
    test_mask = [i in test_indices for i in chunk_indices]

    train_chunk = chunk[train_mask]
    test_chunk = chunk[test_mask]

    # Write train data
    train_chunk.to_csv(
        train_file,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False
    )

    # Write test data
    test_chunk.to_csv(
        test_file,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False
    )

    first_chunk = False

    print(f"Processed rows {start} to {end}")

print("\nTrain-Test split completed!")

print("Train file:", train_file)
print("Test file:", test_file)