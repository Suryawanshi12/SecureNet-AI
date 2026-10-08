from fastapi.testclient import TestClient
from backend.main import app
from backend.db import SessionLocal
from backend.auth.models import User
import time
import sys

client = TestClient(app)

def run_tests():
    db = SessionLocal()
    random_id = int(time.time())
    email = f"testuser_{random_id}@example.com"
    password = "SuperSecretPassword123!"
    
    print("=== STARTING TESTS ===")
    
    # 1. Register new user
    res1 = client.post("/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": password
    })
    print("1. Register:", res1.status_code, "PASS" if res1.status_code in [200, 201] else "FAIL")
    
    # 2. Register same email again
    res2 = client.post("/auth/register", json={
        "full_name": "Test User 2",
        "email": email,
        "password": password
    })
    print("2. Duplicate Register:", res2.status_code, "PASS" if res2.status_code == 400 else "FAIL")
    
    # 3. Login with correct password
    res3 = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    print("3. Login Correct:", res3.status_code, "PASS" if res3.status_code == 200 else "FAIL")
    token = res3.json().get("access_token") if res3.status_code == 200 else "INVALID"
    
    # 4. Login with wrong password
    res4 = client.post("/auth/login", json={
        "email": email,
        "password": "WrongPassword!"
    })
    print("4. Login Wrong Password:", res4.status_code, "PASS" if res4.status_code == 401 else "FAIL")
    
    # 5. GET /auth/me with valid JWT
    res5 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("5. GET /auth/me valid JWT:", res5.status_code, "PASS" if res5.status_code == 200 else "FAIL")
    
    # 6. GET /auth/me without JWT
    res6 = client.get("/auth/me")
    print("6. GET /auth/me no JWT:", res6.status_code, "PASS" if res6.status_code == 401 else "FAIL")
    
    # 7. GET /auth/me with invalid JWT
    res7 = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    print("7. GET /auth/me invalid JWT:", res7.status_code, "PASS" if res7.status_code == 401 else "FAIL")
    
    REAL_FEATURES = {
        "Destination Port": 80, "Flow Duration": 1000, "Total Fwd Packets": 5,
        "Total Backward Packets": 5, "Total Length of Fwd Packets": 500,
        "Total Length of Bwd Packets": 500, "Fwd Packet Length Max": 100,
        "Fwd Packet Length Min": 40, "Fwd Packet Length Mean": 70,
        "Fwd Packet Length Std": 30, "Bwd Packet Length Max": 100,
        "Bwd Packet Length Min": 40, "Bwd Packet Length Mean": 70,
        "Bwd Packet Length Std": 30, "Flow Bytes/s": 1000,
        "Flow Packets/s": 10, "Flow IAT Mean": 100, "Flow IAT Std": 10,
        "Flow IAT Max": 200, "Flow IAT Min": 50, "Fwd IAT Total": 500,
        "Fwd IAT Mean": 100, "Fwd IAT Std": 10, "Fwd IAT Max": 200,
        "Fwd IAT Min": 50, "Bwd IAT Total": 500, "Bwd IAT Mean": 100,
        "Bwd IAT Std": 10, "Bwd IAT Max": 200, "Bwd IAT Min": 50,
        "Fwd PSH Flags": 0, "Bwd PSH Flags": 0, "Fwd URG Flags": 0,
        "Bwd URG Flags": 0, "Fwd Header Length": 20, "Bwd Header Length": 20,
        "Fwd Packets/s": 5, "Bwd Packets/s": 5, "Min Packet Length": 40,
        "Max Packet Length": 100, "Packet Length Mean": 70,
        "Packet Length Std": 30, "Packet Length Variance": 900,
        "FIN Flag Count": 0, "SYN Flag Count": 1, "RST Flag Count": 0,
        "PSH Flag Count": 0, "ACK Flag Count": 5, "URG Flag Count": 0,
        "CWE Flag Count": 0, "ECE Flag Count": 0, "Down/Up Ratio": 1,
        "Average Packet Size": 70, "Avg Fwd Segment Size": 70,
        "Avg Bwd Segment Size": 70, "Fwd Avg Bytes/Bulk": 0,
        "Fwd Avg Packets/Bulk": 0, "Fwd Avg Bulk Rate": 0,
        "Bwd Avg Bytes/Bulk": 0, "Bwd Avg Packets/Bulk": 0,
        "Bwd Avg Bulk Rate": 0, "Subflow Fwd Packets": 5,
        "Subflow Fwd Bytes": 350, "Subflow Bwd Packets": 5,
        "Subflow Bwd Bytes": 350, "Init_Win_bytes_forward": 8192,
        "Init_Win_bytes_backward": 8192, "act_data_pkt_fwd": 4,
        "min_seg_size_forward": 20, "Active Mean": 100, "Active Std": 10,
        "Active Max": 200, "Active Min": 50, "Idle Mean": 1000,
        "Idle Std": 100, "Idle Max": 2000, "Idle Min": 500,
        "Fwd Header Length.1": 20
    }
    
    # 8. POST /predict with valid JWT
    res8 = client.post("/predict", json={"features": REAL_FEATURES},
        headers={"Authorization": f"Bearer {token}"})
    print("8. POST /predict valid JWT:", res8.status_code, "PASS" if res8.status_code == 200 else "FAIL")
    if res8.status_code != 200:
        print("   ->", res8.text)
        
    # 9. POST /predict without JWT
    res9 = client.post("/predict", json={"features": REAL_FEATURES})
    print("9. POST /predict no JWT:", res9.status_code, "PASS" if res9.status_code == 401 else "FAIL")
    
    # 10. Verify PostgreSQL users table password_hash
    db_user = db.query(User).filter(User.email == email).first()
    is_argon2 = db_user.password_hash.startswith("$argon2")
    is_plain = db_user.password_hash == password
    print("10. Postgres Password Hash:", "PASS" if is_argon2 and not is_plain else "FAIL", f"(Starts with $argon2: {is_argon2})")
    
    # Clean up
    db.delete(db_user)
    db.commit()
    db.close()

if __name__ == "__main__":
    run_tests()
