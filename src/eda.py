import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# SECURENET AI - EXPLORATORY DATA ANALYSIS
# ============================================================

print("=" * 80)
print("SECURENET AI - EXPLORATORY DATA ANALYSIS")
print("=" * 80)

# ------------------------------------------------------------
# 1. FILE PATH
# ------------------------------------------------------------

file_path = "data/processed/master_dataset.csv"

print("\n[1] Loading dataset...")
print(f"File: {file_path}")

# Check whether file exists
if not os.path.exists(file_path):
    print("\nERROR: Dataset file not found!")
    print("Make sure master_dataset.csv exists inside:")
    print("data/processed/")
    exit()

# Load dataset
df = pd.read_csv(file_path, low_memory=False)

print("Dataset loaded successfully!")

# ------------------------------------------------------------
# 2. DATASET SHAPE
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[2] DATASET SHAPE")
print("=" * 80)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")
print(f"Shape   : {df.shape}")

# ------------------------------------------------------------
# 3. COLUMN NAMES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[3] COLUMN NAMES")
print("=" * 80)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:2}. {column}")

# ------------------------------------------------------------
# 4. FIRST 5 ROWS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[4] FIRST 5 ROWS")
print("=" * 80)

print(df.head())

# ------------------------------------------------------------
# 5. DATA TYPES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[5] DATA TYPES")
print("=" * 80)

print(df.dtypes)

print("\nData type summary:")
print(df.dtypes.value_counts())

# ------------------------------------------------------------
# 6. LABEL DISTRIBUTION
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[6] LABEL DISTRIBUTION")
print("=" * 80)

# Make sure Label column exists
if "Label" not in df.columns:
    print("ERROR: 'Label' column not found!")
    print("Available columns:")
    print(df.columns.tolist())
    exit()

label_counts = df["Label"].value_counts()

print(label_counts)

# ------------------------------------------------------------
# 7. LABEL PERCENTAGES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[7] LABEL PERCENTAGES")
print("=" * 80)

label_percentages = (
    df["Label"]
    .value_counts(normalize=True)
    .mul(100)
    .round(4)
)

label_summary = pd.DataFrame({
    "Count": label_counts,
    "Percentage": label_percentages
})

print(label_summary)

# ------------------------------------------------------------
# 8. NUMBER OF UNIQUE LABELS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[8] UNIQUE LABELS")
print("=" * 80)

print(f"Number of unique labels: {df['Label'].nunique()}")

print("\nLabels:")
for label in df["Label"].unique():
    print(f"- {label}")

# ------------------------------------------------------------
# 9. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[9] MISSING VALUES")
print("=" * 80)

missing_values = df.isnull().sum()

total_missing = missing_values.sum()

print(f"Total missing values: {total_missing:,}")

if total_missing > 0:
    print("\nColumns containing missing values:")
    print(missing_values[missing_values > 0])
else:
    print("No missing values found.")

# ------------------------------------------------------------
# 10. INFINITE VALUES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[10] INFINITE VALUES")
print("=" * 80)

numeric_columns = df.select_dtypes(include=np.number).columns

infinite_values = np.isinf(df[numeric_columns]).sum()

total_infinite = infinite_values.sum()

print(f"Total infinite values: {total_infinite:,}")

if total_infinite > 0:
    print("\nColumns containing infinite values:")
    print(infinite_values[infinite_values > 0])
else:
    print("No infinite values found.")

# ------------------------------------------------------------
# 11. DUPLICATE ROWS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[11] DUPLICATE ROWS")
print("=" * 80)

duplicate_rows = df.duplicated().sum()

print(f"Duplicate rows: {duplicate_rows:,}")

if duplicate_rows == 0:
    print("No duplicate rows found.")
else:
    print("Duplicate rows exist in the dataset.")

# ------------------------------------------------------------
# 12. BASIC STATISTICS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[12] BASIC STATISTICS")
print("=" * 80)

print(df.describe())

# ------------------------------------------------------------
# 13. DATASET MEMORY USAGE
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[13] MEMORY USAGE")
print("=" * 80)

memory_usage = df.memory_usage(deep=True).sum()

print(f"Memory usage: {memory_usage / (1024 ** 2):.2f} MB")

# ------------------------------------------------------------
# 14. BENIGN vs ATTACK TRAFFIC
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[14] BENIGN vs ATTACK TRAFFIC")
print("=" * 80)

benign_count = (df["Label"] == "BENIGN").sum()
attack_count = len(df) - benign_count

print(f"BENIGN traffic : {benign_count:,}")
print(f"ATTACK traffic : {attack_count:,}")

benign_percentage = (benign_count / len(df)) * 100
attack_percentage = (attack_count / len(df)) * 100

print(f"\nBENIGN percentage : {benign_percentage:.2f}%")
print(f"ATTACK percentage : {attack_percentage:.2f}%")

# ------------------------------------------------------------
# 15. SAVE LABEL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[15] SAVING EDA RESULTS")
print("=" * 80)

os.makedirs("reports", exist_ok=True)

label_summary_path = "reports/label_distribution.csv"

label_summary.to_csv(label_summary_path)

print(f"Label distribution saved to:")
print(label_summary_path)

# ------------------------------------------------------------
# 16. CREATE LABEL DISTRIBUTION GRAPH
# ------------------------------------------------------------

print("\nCreating label distribution graph...")

plt.figure(figsize=(14, 8))

label_counts.sort_values(ascending=True).plot(
    kind="barh"
)

plt.title("CICIDS2017 - Network Traffic Label Distribution")
plt.xlabel("Number of Samples")
plt.ylabel("Traffic Label")

plt.tight_layout()

plot_path = "reports/label_distribution.png"

plt.savefig(plot_path, dpi=300)

plt.close()

print(f"Graph saved to:")
print(plot_path)

# ------------------------------------------------------------
# 17. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 80)

print(f"""
Dataset:
    Rows              : {len(df):,}
    Columns           : {len(df.columns)}
    Unique Labels     : {df['Label'].nunique()}
    Missing Values    : {total_missing:,}
    Infinite Values   : {total_infinite:,}
    Duplicate Rows    : {duplicate_rows:,}

Traffic:
    BENIGN            : {benign_count:,} ({benign_percentage:.2f}%)
    ATTACK            : {attack_count:,} ({attack_percentage:.2f}%)

Reports:
    {label_summary_path}
    {plot_path}
""")

print("=" * 80)