"""
backend/realtime/test_detection_store.py
=========================================
Tests for DetectionStore using an in-memory SQLite session.
No live PostgreSQL connection is required.

Tests cover:
  1. Valid real-time result stored correctly (all fields verified)
  2. None input is safely rejected (no DB write)
  3. Invalid/incomplete result with bad risk_level is rejected
  4. Result with out-of-range confidence is rejected
  5. Flow metadata (source_ip, dest_ip, protocol) is persisted
  6. packet_count is persisted
  7. Raw payload is confirmed absent from Detection ORM model
  8. DB error is handled gracefully (rollback, returns None)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db import Base
from backend.detection.models import Detection
from backend.realtime.realtime_detector import RealtimeDetectionResult
from backend.realtime.detection_store import store_realtime_detection, _is_valid_result


# ---------------------------------------------------------------------------
# In-memory SQLite test fixture
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Creates an isolated in-memory SQLite session per test."""
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _make_result(**overrides) -> RealtimeDetectionResult:
    """Build a default valid RealtimeDetectionResult with optional overrides."""
    defaults = dict(
        flow_id="192.168.1.10:45000-10.0.0.5:443-TCP",
        source_ip="192.168.1.10",
        source_port=45000,
        destination_ip="10.0.0.5",
        destination_port=443,
        protocol="TCP",
        packet_count=8,
        total_bytes=1200,
        prediction="BENIGN",
        confidence=97.5,
        attack_severity=0,
        anomaly_score=0.0,
        risk_score=2.1,
        risk_level="LOW",
        explanation=[{"feature": "Destination Port", "shap_value": 0.3, "direction": "decreased"}],
    )
    defaults.update(overrides)
    return RealtimeDetectionResult(**defaults)


# ---------------------------------------------------------------------------
# TEST 1: Valid result stored with all core ML fields
# ---------------------------------------------------------------------------

def test_valid_result_is_stored(db_session):
    """A valid RealtimeDetectionResult must be inserted into the DB."""
    result = _make_result()
    saved = store_realtime_detection(result, db=db_session)

    assert saved is not None
    assert isinstance(saved, Detection)
    assert saved.id is not None
    assert saved.prediction == "BENIGN"
    assert saved.confidence == 97.5
    assert saved.attack_severity == 0
    assert saved.anomaly_score == 0.0
    assert saved.risk_score == 2.1
    assert saved.risk_level == "LOW"
    assert saved.shap_values == [{"feature": "Destination Port", "shap_value": 0.3, "direction": "decreased"}]


# ---------------------------------------------------------------------------
# TEST 2: None input is safely rejected — zero DB writes
# ---------------------------------------------------------------------------

def test_none_result_is_rejected(db_session):
    """store_realtime_detection(None) must return None without touching the DB."""
    saved = store_realtime_detection(None, db=db_session)
    assert saved is None

    count = db_session.query(Detection).count()
    assert count == 0


# ---------------------------------------------------------------------------
# TEST 3: Invalid risk_level is rejected
# ---------------------------------------------------------------------------

def test_invalid_risk_level_is_rejected(db_session):
    """A result with an unknown risk_level must be rejected before DB insert."""
    result = _make_result(risk_level="UNKNOWN")
    saved = store_realtime_detection(result, db=db_session)
    assert saved is None

    count = db_session.query(Detection).count()
    assert count == 0


# ---------------------------------------------------------------------------
# TEST 4: Out-of-range confidence is rejected
# ---------------------------------------------------------------------------

def test_out_of_range_confidence_rejected(db_session):
    """confidence=150.0 must fail validation and not be stored."""
    result = _make_result(confidence=150.0)
    saved = store_realtime_detection(result, db=db_session)
    assert saved is None


# ---------------------------------------------------------------------------
# TEST 5: Flow metadata columns (IP, port, protocol) are persisted
# ---------------------------------------------------------------------------

def test_flow_metadata_is_persisted(db_session):
    """source_ip, destination_ip, source_port, destination_port, protocol must be stored."""
    result = _make_result(
        source_ip="172.16.0.1",
        destination_ip="8.8.8.8",
        source_port=60000,
        destination_port=53,
        protocol="UDP",
    )
    saved = store_realtime_detection(result, db=db_session)

    assert saved is not None
    assert saved.source_ip == "172.16.0.1"
    assert saved.destination_ip == "8.8.8.8"
    assert saved.source_port == 60000
    assert saved.destination_port == 53
    assert saved.protocol == "UDP"


# ---------------------------------------------------------------------------
# TEST 6: packet_count is persisted
# ---------------------------------------------------------------------------

def test_packet_count_is_persisted(db_session):
    """packet_count from the flow must be stored in the detection record."""
    result = _make_result(packet_count=42)
    saved = store_realtime_detection(result, db=db_session)

    assert saved is not None
    assert saved.packet_count == 42


# ---------------------------------------------------------------------------
# TEST 7: Raw packet payload is NEVER on the model
# ---------------------------------------------------------------------------

def test_no_raw_payload_field_on_model():
    """
    The Detection ORM model must NOT have any payload/content/data field.
    This confirms raw packet data cannot be stored.
    """
    prohibited = {"payload", "content", "packet_data", "raw", "body", "data"}
    model_columns = {c.name for c in Detection.__table__.columns}
    intersection = prohibited & model_columns
    assert not intersection, (
        f"Forbidden payload field(s) found on Detection model: {intersection}"
    )


# ---------------------------------------------------------------------------
# TEST 8: DB error is handled gracefully
# ---------------------------------------------------------------------------

def test_db_error_handled_gracefully(db_session, monkeypatch):
    """If db.commit() raises, store_realtime_detection returns None (no crash)."""
    def bad_commit():
        raise RuntimeError("Simulated DB commit failure")

    monkeypatch.setattr(db_session, "commit", bad_commit)

    result = _make_result()
    saved = store_realtime_detection(result, db=db_session)
    assert saved is None
