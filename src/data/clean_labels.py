import pandas as pd

input_file = "data/processed/master_dataset.csv"
output_file = "data/processed/master_dataset_clean.csv"

df = pd.read_csv(input_file, low_memory=False)

df["Label"] = df["Label"].astype(str).str.strip()

df["Label"] = df["Label"].str.replace("�", "-", regex=False)

df["Label"] = df["Label"].str.replace(r"\s+", " ", regex=True)

df.to_csv(output_file, index=False)

print("Label cleaning completed!")
print("Saved to:", output_file)
print("\nLabels:")
print(df["Label"].value_counts())