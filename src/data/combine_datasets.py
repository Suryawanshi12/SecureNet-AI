import pandas as pd
import os

# ============================================================
# SECURENET AI - COMBINE ALL CLEANED DATASETS
# ============================================================

print("=" * 80)
print("SECURENET AI - COMBINING ALL CLEANED DATASETS")
print("=" * 80)

processed_folder = "data/processed"

files = [
    "cleaned_Monday-WorkingHours.pcap_ISCX.csv",
    "cleaned_Tuesday-WorkingHours.pcap_ISCX.csv",
    "cleaned_Wednesday-workingHours.pcap_ISCX.csv",
    "cleaned_Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "cleaned_Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "cleaned_Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "cleaned_Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "cleaned_Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
]

dataframes = []

# ------------------------------------------------------------
# 1. LOAD ALL DATASETS
# ------------------------------------------------------------

for file_name in files:

    file_path = os.path.join(processed_folder, file_name)

    print("\nLoading:")
    print(file_name)

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND")
        continue

    df = pd.read_csv(file_path, low_memory=False)

    print(f"Rows loaded: {len(df):,}")

    dataframes.append(df)

# ------------------------------------------------------------
# 2. COMBINE DATASETS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[2] COMBINING DATASETS")
print("=" * 80)

master_df = pd.concat(
    dataframes,
    ignore_index=True
)

print(f"Rows before duplicate removal : {len(master_df):,}")
print(f"Columns                       : {len(master_df.columns)}")

# ------------------------------------------------------------
# 3. REMOVE CROSS-DATASET DUPLICATES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[3] REMOVING CROSS-DATASET DUPLICATES")
print("=" * 80)

duplicate_count = master_df.duplicated().sum()

print(f"Duplicate rows found: {duplicate_count:,}")

master_df = master_df.drop_duplicates()

print(
    f"Rows after duplicate removal: "
    f"{len(master_df):,}"
)

# ------------------------------------------------------------
# 4. CHECK LABELS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("[4] FINAL LABEL DISTRIBUTION")
print("=" * 80)

label_counts = master_df["Label"].value_counts()

print(label_counts)

# ------------------------------------------------------------
# 5. SAVE MASTER DATASET
# ------------------------------------------------------------

output_file = "data/processed/master_dataset.csv"

print("\n" + "=" * 80)
print("[5] SAVING MASTER DATASET")
print("=" * 80)

master_df.to_csv(
    output_file,
    index=False
)

print(f"Master dataset saved to:")
print(output_file)

print(f"\nFinal rows    : {len(master_df):,}")
print(f"Final columns : {len(master_df.columns)}")

print("\n" + "=" * 80)
print("MASTER DATASET CREATED SUCCESSFULLY")
print("=" * 80)