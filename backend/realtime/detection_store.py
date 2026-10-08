"""
backend/realtime/detection_store.py
====================================
Persists RealtimeDetectionResult objects into the existing PostgreSQL
`detections` table using the existing SQLAlchemy Session infrastructure.

Design principles:
- Reuses backend.db.SessionLocal and backend.detection.models.Detection
- ALL new flow-metadata columns (source_ip, dest_ip, protocol, etc.) are nullable,
  so existing /predict endpoint rows are completely unaffected.
- Raw packet payload is NEVER stored (only headers/metadata derived from the flow).
- Invalid / incomplete results are rejected before any DB write.
- DB errors are caught and logged; the pipeline continues regardless.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.db import SessionLocal
from backend.detection.models import Detection
from backend.realtime.realtime_detector import RealtimeDetectionResult

logger = logging.getLogger("DetectionStore")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def store_realtime_detection(
    result: RealtimeDetectionResult,
    db: Optional[Session] = None,
) -> Optional[Detection]:
    """
    Persist a valid RealtimeDetectionResult into the `detections` table.

    Args:
        result: A fully populated RealtimeDetectionResult from RealtimeDetector.
        db:     Optional external SQLAlchemy Session (useful for testing).
                If None, a new SessionLocal session is created and closed here.

    Returns:
        The saved Detection ORM object with its auto-generated id,
        or None if the result was rejected or a DB error occurred.

    Safety guarantees:
        - Returns None immediately for None input (no DB interaction).
        - Returns None if core ML fields are missing/invalid.
        - Raw packet payload is never stored (not present on RealtimeDetectionResult).
        - DB errors are caught and logged; they never propagate to the caller.
    """
    # ── Guard: never store None ──────────────────────────────────────────────
    if result is None:
        logger.warning("store_realtime_detection: received None result — skipping.")
        return None

    # ── Guard: validate core ML fields ──────────────────────────────────────
    if not _is_valid_result(result):
        logger.warning(
            f"store_realtime_detection: result for flow '{result.flow_id}' "
            "failed validation — skipping DB insert."
        )
        return None

    # ── Determine session ownership ──────────────────────────────────────────
    owns_session = db is None
    if owns_session:
        db = SessionLocal()

    try:
        detection = Detection(
            # Core ML fields (always present)
            prediction=result.prediction,
            confidence=result.confidence,
            attack_severity=result.attack_severity,
            anomaly_score=result.anomaly_score,
            risk_score=result.risk_score,
            risk_level=result.risk_level,
            shap_values=result.explanation or None,

            # Real-time flow metadata (nullable; raw payload is NEVER stored)
            source_ip=result.source_ip or None,
            destination_ip=result.destination_ip or None,
            source_port=result.source_port or None,
            destination_port=result.destination_port or None,
            protocol=result.protocol or None,
            flow_duration_us=getattr(result, "flow_duration_us", None),
            packet_count=result.packet_count or None,
        )

        db.add(detection)
        db.commit()
        db.refresh(detection)

        logger.info(
            f"Stored detection id={detection.id} | flow={result.flow_id} | "
            f"prediction={result.prediction} | risk={result.risk_level}"
        )
        return detection

    except Exception as exc:
        logger.error(
            f"DB error storing detection for flow '{result.flow_id}': {exc}"
        )
        try:
            db.rollback()
        except Exception:
            pass
        return None

    finally:
        if owns_session:
            db.close()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_valid_result(result: RealtimeDetectionResult) -> bool:
    """
    Returns True only when every mandatory ML field is present and in range.
    Incomplete or fake detection results are rejected here — never stored.
    """
    if not isinstance(result.prediction, str) or not result.prediction.strip():
        logger.warning("Validation failed: prediction is empty or not a string.")
        return False

    if not (0.0 <= result.confidence <= 100.0):
        logger.warning(f"Validation failed: confidence={result.confidence} out of [0,100].")
        return False

    if not (0 <= result.attack_severity <= 100):
        logger.warning(f"Validation failed: attack_severity={result.attack_severity}.")
        return False

    if not (0.0 <= result.anomaly_score <= 100.0):
        logger.warning(f"Validation failed: anomaly_score={result.anomaly_score}.")
        return False

    if not (0.0 <= result.risk_score <= 100.0):
        logger.warning(f"Validation failed: risk_score={result.risk_score}.")
        return False

    if result.risk_level not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        logger.warning(f"Validation failed: unknown risk_level='{result.risk_level}'.")
        return False

    return True
