import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app
from backend.detection.models import Detection
from backend.db import SessionLocal
from backend.auth.service import create_access_token
from backend.auth.models import User

def verify_all():
    client = TestClient(app)
    db = SessionLocal()

    # Get or create test user for auth dependency
    user = db.query(User).first()
    if not user:
        print("No user found in database, creating test user.")
        user = User(username="testuser", email="test@example.com", hashed_password="fakehash")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id, user.email, user.role)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Verify schema on live PostgreSQL
    from sqlalchemy import text
    with db.bind.connect() as conn:
        rows = conn.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='detections' AND column_name='shap_values'"
        )).fetchall()
        print(f"Schema check for shap_values column: {rows}")
        assert len(rows) == 1, "shap_values column missing from PostgreSQL detections table!"

    # 2. Add a sample detection with shap_values if needed
    det = Detection(
        prediction="DoSSlowloris",
        confidence=99.5,
        attack_severity=85,
        anomaly_score=0.82,
        risk_score=91.0,
        risk_level="CRITICAL",
        shap_values=[{"feature": "Flow Duration", "value": 5200.0, "shap_value": 0.45, "direction": "increased"}]
    )
    db.add(det)
    db.commit()
    db.refresh(det)
    det_id = det.id
    print(f"Inserted sample detection id={det_id} with shap_values.")

    # Add a sample detection with NULL shap_values
    det_null = Detection(
        prediction="BENIGN",
        confidence=98.0,
        attack_severity=0,
        anomaly_score=0.0,
        risk_score=5.0,
        risk_level="LOW",
        shap_values=None
    )
    db.add(det_null)
    db.commit()
    db.refresh(det_null)
    det_null_id = det_null.id
    print(f"Inserted sample detection id={det_null_id} with NULL shap_values.")

    # 3. Test GET /dashboard/recent-detections
    resp = client.get("/dashboard/recent-detections", headers=headers)
    print(f"GET /dashboard/recent-detections status: {resp.status_code}")
    assert resp.status_code == 200, f"Error response: {resp.text}"
    recent = resp.json()
    assert isinstance(recent, list)
    print(f"Returned {len(recent)} recent detections.")
    found_shap = any("shap_values" in r for r in recent)
    assert found_shap, "shap_values key missing from recent-detections response!"
    print("[OK] GET /dashboard/recent-detections verified successfully.")

    # 4. Test GET /dashboard/detections/{id} for record with shap_values
    resp_detail = client.get(f"/dashboard/detections/{det_id}", headers=headers)
    print(f"GET /dashboard/detections/{det_id} status: {resp_detail.status_code}")
    assert resp_detail.status_code == 200
    data_detail = resp_detail.json()
    assert data_detail["shap_values"] == [{"feature": "Flow Duration", "value": 5200.0, "shap_value": 0.45, "direction": "increased"}]
    print(f"[OK] GET /dashboard/detections/{det_id} verified successfully with shap_values.")

    # 5. Test GET /dashboard/detections/{id} for record with NULL shap_values
    resp_null = client.get(f"/dashboard/detections/{det_null_id}", headers=headers)
    print(f"GET /dashboard/detections/{det_null_id} status: {resp_null.status_code}")
    assert resp_null.status_code == 200
    data_null = resp_null.json()
    assert data_null["shap_values"] is None
    print(f"[OK] GET /dashboard/detections/{det_null_id} verified successfully with NULL shap_values.")

    print("\nALL BACKEND API AND SCHEMA VERIFICATIONS PASSED!")

if __name__ == "__main__":
    verify_all()
