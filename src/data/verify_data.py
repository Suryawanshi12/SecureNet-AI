import pandas as pd
import numpy as np
import os

# ============================================================
# SETTINGS
# ============================================================

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

# ============================================================
# START
# ============================================================

print("=" * 80)
print("SECURENET AI - PREPROCESSED DATA VERIFICATION")
print("=" * 80)

all_passed = True

for file_name in files:

    print("\n" + "=" * 80)
    print(f"CHECKING: {file_name}")
    print("=" * 80)

    file_path = os.path.join(processed_folder, file_name)

    # --------------------------------------------------------
    # Check file exists
    # --------------------------------------------------------

    if not os.path.exists(file_path):
        print("❌ FILE NOT FOUND")
        all_passed = False
        continue

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(file_path, low_memory=False)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    # --------------------------------------------------------
    # 1. Column check
    # --------------------------------------------------------

    expected_columns = 79

    if len(df.columns) == expected_columns:
        print("✅ Column count: PASS")
    else:
        print(f"❌ Column count: FAIL - expected {expected_columns}")
        all_passed = False

    # --------------------------------------------------------
    # 2. Label column
    # --------------------------------------------------------

    if "Label" in df.columns:
        print("✅ Label column: PASS")
    else:
        print("❌ Label column: FAIL")
        all_passed = False

    # --------------------------------------------------------
    # 3. Missing values
    # --------------------------------------------------------

    missing_values = df.isnull().sum().sum()

    print(f"Missing values: {missing_values:,}")

    if missing_values == 0:
        print("✅ Missing values: PASS")
    else:
        print("❌ Missing values: FAIL")
        all_passed = False

    # --------------------------------------------------------
    # 4. Infinite values
    # --------------------------------------------------------

    numeric_columns = df.select_dtypes(include=np.number).columns

    infinity_values = np.isinf(
        df[numeric_columns]
    ).sum().sum()

    print(f"Infinite values: {infinity_values:,}")

    if infinity_values == 0:
        print("✅ Infinite values: PASS")
    else:
        print("❌ Infinite values: FAIL")
        all_passed = False

    # --------------------------------------------------------
    # 5. Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_rows:,}")

    if duplicate_rows == 0:
        print("✅ Duplicate rows: PASS")
    else:
        print("❌ Duplicate rows: FAIL")
        all_passed = False

    # --------------------------------------------------------
    # 6. Negative Flow Duration
    # --------------------------------------------------------

    if "Flow Duration" in df.columns:

        negative_duration = (
            df["Flow Duration"] < 0
        ).sum()

        print(
            f"Negative Flow Duration: "
            f"{negative_duration:,}"
        )

        if negative_duration == 0:
            print("✅ Flow Duration: PASS")
        else:
            print("❌ Flow Duration: FAIL")
            all_passed = False

    # --------------------------------------------------------
    # 7. Empty labels
    # --------------------------------------------------------

    if "Label" in df.columns:

        empty_labels = (
            df["Label"]
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        print(f"Empty labels: {empty_labels:,}")

        if empty_labels == 0:
            print("✅ Labels: PASS")
        else:
            print("❌ Labels: FAIL")
            all_passed = False

    # --------------------------------------------------------
    # 8. Label distribution
    # --------------------------------------------------------

    print("\nLabel distribution:")

    print(df["Label"].value_counts())

# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 80)
print("FINAL VERIFICATION RESULT")
print("=" * 80)

if all_passed:
    print("✅ ALL PREPROCESSED DATASETS PASSED!")
    print("Your datasets are ready for the next stage.")
else:
    print("❌ SOME DATASETS FAILED VERIFICATION.")
    print("Check the errors shown above.")

print("=" * 80)