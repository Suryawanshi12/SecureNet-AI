import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.auth.models import User

BASE = "http://127.0.0.1:8000"
EMAIL = f"e2e_{int(time.time())}@securenet.ai"
PASSWORD = "Test@E2E!2025"
FULL_NAME = "E2E Test User"
results = {}

FEATS = {
    "Destination Port": 80, "Flow Duration": 1000, "Total Fwd Packets": 5,
    "Total Backward Packets": 5, "Total Length of Fwd Packets": 500,
    "Total Length of Bwd Packets": 500, "Fwd Packet Length Max": 100,
    "Fwd Packet Length Min": 40, "Fwd Packet Length Mean": 70,
    "Fwd Packet Length Std": 30, "Bwd Packet Length Max": 100,
    "Bwd Packet Length Min": 40, "Bwd Packet Length Mean": 70,
    "Bwd Packet Length Std": 30, "Flow Bytes/s": 1000, "Flow Packets/s": 10,
    "Flow IAT Mean": 100, "Flow IAT Std": 10, "Flow IAT Max": 200,
    "Flow IAT Min": 50, "Fwd IAT Total": 500, "Fwd IAT Mean": 100,
    "Fwd IAT Std": 10, "Fwd IAT Max": 200, "Fwd IAT Min": 50,
    "Bwd IAT Total": 500, "Bwd IAT Mean": 100, "Bwd IAT Std": 10,
    "Bwd IAT Max": 200, "Bwd IAT Min": 50, "Fwd PSH Flags": 0,
    "Bwd PSH Flags": 0, "Fwd URG Flags": 0, "Bwd URG Flags": 0,
    "Fwd Header Length": 20, "Bwd Header Length": 20, "Fwd Packets/s": 5,
    "Bwd Packets/s": 5, "Min Packet Length": 40, "Max Packet Length": 100,
    "Packet Length Mean": 70, "Packet Length Std": 30,
    "Packet Length Variance": 900, "FIN Flag Count": 0, "SYN Flag Count": 1,
    "RST Flag Count": 0, "PSH Flag Count": 0, "ACK Flag Count": 5,
    "URG Flag Count": 0, "CWE Flag Count": 0, "ECE Flag Count": 0,
    "Down/Up Ratio": 1, "Average Packet Size": 70, "Avg Fwd Segment Size": 70,
    "Avg Bwd Segment Size": 70, "Fwd Avg Bytes/Bulk": 0,
    "Fwd Avg Packets/Bulk": 0, "Fwd Avg Bulk Rate": 0,
    "Bwd Avg Bytes/Bulk": 0, "Bwd Avg Packets/Bulk": 0,
    "Bwd Avg Bulk Rate": 0, "Subflow Fwd Packets": 5, "Subflow Fwd Bytes": 350,
    "Subflow Bwd Packets": 5, "Subflow Bwd Bytes": 350,
    "Init_Win_bytes_forward": 8192, "Init_Win_bytes_backward": 8192,
    "act_data_pkt_fwd": 4, "min_seg_size_forward": 20, "Active Mean": 100,
    "Active Std": 10, "Active Max": 200, "Active Min": 50, "Idle Mean": 1000,
    "Idle Std": 100, "Idle Max": 2000, "Idle Min": 500,
    "Fwd Header Length.1": 20,
}


def ck(label, cond, extra=""):
    s = "PASS" if cond else "FAIL"
    results[label] = s
    suffix = f" | {extra}" if extra else ""
    print(f"  [{s}] {label}{suffix}")


print("=== SecureNet AI Full Auth E2E Test ===")

# 1. Register
print("1. Register new user")
r = requests.post(f"{BASE}/auth/register", json={
    "full_name": FULL_NAME, "email": EMAIL, "password": PASSWORD})
ck("Register new user", r.status_code == 200, f"HTTP {r.status_code}")
if r.ok:
    d = r.json()
    ck("  id returned", "id" in d)
    ck("  email matches", d.get("email") == EMAIL)
    ck("  no password_hash in response", "password_hash" not in d)

# 2. Duplicate
print("2. Duplicate email -> 400")
r2 = requests.post(f"{BASE}/auth/register", json={
    "full_name": FULL_NAME, "email": EMAIL, "password": PASSWORD})
ck("Duplicate email -> 400", r2.status_code == 400, f"HTTP {r2.status_code}")

# 3. Login correct
print("3. Login correct credentials")
r3 = requests.post(f"{BASE}/auth/login", json={"email": EMAIL, "password": PASSWORD})
ck("Login correct -> 200", r3.status_code == 200, f"HTTP {r3.status_code}")
token = None
if r3.ok:
    b = r3.json()
    token = b.get("access_token")
    ck("  access_token (starts ey)", bool(token and token.startswith("ey")), (token or "")[:30])
    ck("  token_type bearer", b.get("token_type") == "bearer")
    ck("  user.email matches", b.get("user", {}).get("email") == EMAIL)

# 4. Wrong password
print("4. Wrong password -> 401")
r4 = requests.post(f"{BASE}/auth/login", json={"email": EMAIL, "password": "WrongPass!"})
ck("Wrong password -> 401", r4.status_code == 401, f"HTTP {r4.status_code}")

hdrs = {"Authorization": f"Bearer {token}"}

# 5. /auth/me valid JWT
print("5. GET /auth/me with valid JWT")
r5 = requests.get(f"{BASE}/auth/me", headers=hdrs)
ck("/auth/me valid JWT -> 200", r5.status_code == 200, f"HTTP {r5.status_code}")
if r5.ok:
    ck("  email in /auth/me matches", r5.json().get("email") == EMAIL)

# 6. /auth/me no JWT
print("6. GET /auth/me without JWT -> 401")
r6 = requests.get(f"{BASE}/auth/me")
ck("/auth/me no JWT -> 401", r6.status_code == 401, f"HTTP {r6.status_code}")

# 7. /auth/me invalid JWT
print("7. GET /auth/me invalid JWT -> 401")
r7 = requests.get(f"{BASE}/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
ck("/auth/me invalid JWT -> 401", r7.status_code == 401, f"HTTP {r7.status_code}")

# 8. /predict with valid JWT
print("8. POST /predict with valid JWT")
r8 = requests.post(f"{BASE}/predict", json={"features": FEATS}, headers=hdrs)
ck("/predict valid JWT -> 200", r8.status_code == 200, f"HTTP {r8.status_code}")
if r8.ok:
    ck("  prediction field present", "prediction" in r8.json())

# 9. /predict without JWT
print("9. POST /predict without JWT -> 401")
r9 = requests.post(f"{BASE}/predict", json={"features": FEATS})
ck("/predict no JWT -> 401", r9.status_code == 401, f"HTTP {r9.status_code}")

# 10. DB check + logout simulation
print("10. DB hash check + logout simulation")
engine = create_engine("postgresql://postgres:shruti1506@localhost:5432/securenet_ai")
Sess = sessionmaker(bind=engine)
db = Sess()
u = db.query(User).filter(User.email == EMAIL).first()
is_argon = u is not None and u.password_hash.startswith("$argon2")
ck("Argon2 hash in DB", is_argon, (u.password_hash[:30] if u else "NOT FOUND"))
storage = {"securenet_access_token": token}
storage.pop("securenet_access_token", None)
storage.pop("securenet_user", None)
ck("JWT cleared on logout", storage.get("securenet_access_token") is None)
if u:
    db.delete(u)
    db.commit()
db.close()

print()
print("=" * 42)
print("SUMMARY")
print("=" * 42)
for k, v in results.items():
    if not k.startswith(" "):
        print(f"[{v}] {k}")
