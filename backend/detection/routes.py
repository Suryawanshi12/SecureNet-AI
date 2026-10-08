from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.db import get_db
from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.detection.models import Detection

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# GET /dashboard/stats
# ==========================================

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_traffic = db.query(func.count(Detection.id)).scalar() or 0

    threats_detected = (
        db.query(func.count(Detection.id))
        .filter(Detection.prediction != "BENIGN")
        .scalar() or 0
    )

    # anomalies = rows where anomaly_score > 0 (Isolation Forest flagged them)
    anomalies = (
        db.query(func.count(Detection.id))
        .filter(Detection.anomaly_score > 0)
        .scalar() or 0
    )

    critical_threats = (
        db.query(func.count(Detection.id))
        .filter(Detection.risk_level == "CRITICAL")
        .scalar() or 0
    )

    return {
        "total_traffic": total_traffic,
        "threats_detected": threats_detected,
        "anomalies": anomalies,
        "critical_threats": critical_threats,
    }


# ==========================================
# GET /dashboard/threat-distribution
# ==========================================

@router.get("/threat-distribution")
def get_threat_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = (
        db.query(Detection.prediction, func.count(Detection.id).label("count"))
        .group_by(Detection.prediction)
        .order_by(func.count(Detection.id).desc())
        .all()
    )

    return [{"prediction": r.prediction, "count": r.count} for r in rows]


# ==========================================
# GET /dashboard/risk-distribution
# ==========================================

@router.get("/risk-distribution")
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = (
        db.query(Detection.risk_level, func.count(Detection.id).label("count"))
        .group_by(Detection.risk_level)
        .all()
    )

    level_map = {r.risk_level: r.count for r in rows}

    return [
        {"risk_level": "LOW",      "count": level_map.get("LOW",      0)},
        {"risk_level": "MEDIUM",   "count": level_map.get("MEDIUM",   0)},
        {"risk_level": "HIGH",     "count": level_map.get("HIGH",     0)},
        {"risk_level": "CRITICAL", "count": level_map.get("CRITICAL", 0)},
    ]


# ==========================================
# GET /dashboard/recent-detections
# ==========================================

@router.get("/recent-detections")
def get_recent_detections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = (
        db.query(Detection)
        .order_by(Detection.timestamp.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "prediction": r.prediction,
            "confidence": r.confidence,
            "attack_severity": r.attack_severity,
            "anomaly_score": r.anomaly_score,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "shap_values": r.shap_values,
        }
        for r in rows
    ]


# ==========================================
# GET /dashboard/detections/{detection_id}
# ==========================================

@router.get("/detections/{detection_id}")
def get_detection_by_id(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    row = (
        db.query(Detection)
        .filter(Detection.id == detection_id)
        .first()
    )

    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Detection not found")

    return {
        "id": row.id,
        "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        "prediction": row.prediction,
        "confidence": row.confidence,
        "attack_severity": row.attack_severity,
        "anomaly_score": row.anomaly_score,
        "risk_score": row.risk_score,
        "risk_level": row.risk_level,
        "shap_values": row.shap_values,
    }

