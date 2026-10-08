import pandas as pd
import numpy as np
import os

# ============================================================
# SETTINGS
# ============================================================

file_name  = "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"

input_path = os.path.join("data", "raw", file_name)

output_path = os.path.join(
    "data",
    "processed",
    "cleaned_" + file_name
)

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("SECURENET AI - DATA PREPROCESSING")
print("=" * 70)

print(f"\nLoading: {file_name}")

df = pd.read_csv(input_path, low_memory=False)

print(f"Original rows: {len(df):,}")
print(f"Original columns: {len(df.columns)}")


# ============================================================
# 1. CLEAN COLUMN NAMES
# ============================================================

print("\n[1] Cleaning column names...")

df.columns = df.columns.str.strip()

print("Column names cleaned.")


# ============================================================
# 2. CHECK DUPLICATES
# ============================================================

print("\n[2] Checking duplicate rows...")

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows found: {duplicate_count:,}")

df = df.drop_duplicates()

print(f"Rows after duplicate removal: {len(df):,}")


# ============================================================
# 3. HANDLE INFINITY VALUES
# ============================================================

print("\n[3] Checking infinite values...")

numeric_columns = df.select_dtypes(include=np.number).columns

infinity_count = np.isinf(df[numeric_columns]).sum().sum()

print(f"Infinite values found: {infinity_count:,}")

# Replace infinity with NaN
df[numeric_columns] = df[numeric_columns].replace(
    [np.inf, -np.inf],
    np.nan
)


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\n[4] Checking missing values...")

missing_before = df.isnull().sum().sum()

print(f"Missing values before removal: {missing_before:,}")

# Remove rows containing missing values
df = df.dropna()

missing_after = df.isnull().sum().sum()

print(f"Missing values after removal: {missing_after:,}")


# ============================================================
# 5. CHECK INVALID FLOW DURATION
# ============================================================

print("\n[5] Checking invalid Flow Duration values...")

negative_duration = (df["Flow Duration"] < 0).sum()

print(f"Negative Flow Duration rows: {negative_duration:,}")

if negative_duration > 0:
    df = df[df["Flow Duration"] >= 0]

print(f"Rows after Flow Duration check: {len(df):,}")


# ============================================================
# 6. CHECK LABELS
# ============================================================

print("\n[6] Checking labels...")

print(df["Label"].value_counts())


# ============================================================
# 7. FINAL DATASET INFORMATION
# ============================================================

print("\n[7] FINAL DATASET")

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

print("\nFinal missing values:")
print(df.isnull().sum().sum())

print("\nFinal duplicate rows:")
print(df.duplicated().sum())


# ============================================================
# 8. SAVE CLEANED DATASET
# ============================================================

os.makedirs("data/processed", exist_ok=True)

df.to_csv(output_path, index=False)

print("\n[8] SAVED")

print(f"Output file:")
print(output_path)

print("\n" + "=" * 70)
print("PREPROCESSING COMPLETED")
print("=" * 70)