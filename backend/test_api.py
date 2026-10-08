import pandas as pd
import requests


# ==========================================
# SECURENET AI - API TEST
# ==========================================

API_URL = "http://127.0.0.1:8000/predict"

DATA_PATH = "data/processed/test_encoded.csv"


print("======================================")
print("SECURENET AI - API TEST")
print("======================================")


# ==========================================
# LOAD TEST DATA
# ==========================================

print("\nLoading test dataset...")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print("Dataset loaded!")
print("Total rows:", len(df))


# ==========================================
# SELECT DDoS SAMPLE
# ==========================================

print("\nSelecting DDoS sample...")

ddos_row = df[
    df["Label"] == 2
].iloc[0]

print("Actual Label: DDoS")


# ==========================================
# REMOVE LABEL
# ==========================================

features = ddos_row.drop(
    labels=["Label"]
).to_dict()


# ==========================================
# CREATE API REQUEST
# ==========================================

payload = {
    "features": features
}


# ==========================================
# SEND REQUEST
# ==========================================

print("\nSending request to FastAPI...")

response = requests.post(
    API_URL,
    json=payload
)


# ==========================================
# DISPLAY RESPONSE
# ==========================================

print("\nHTTP Status Code:")
print(response.status_code)


print("\nAPI Response:")

print(
    response.json()
)


print("\n======================================")
print("API TEST COMPLETED")
print("======================================")