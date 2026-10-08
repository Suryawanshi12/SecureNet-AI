import pandas as pd

file_path = "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
print("Loading dataset...")

df = pd.read_csv(file_path, low_memory=False)

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== LABEL DISTRIBUTION =====")
print(df[" Label"].value_counts())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum().sort_values(ascending=False).head(20))

print("\n===== DUPLICATE ROWS =====")
print(df.duplicated().sum())

print("\n===== NUMERICAL SUMMARY =====")
print(df.describe().T)