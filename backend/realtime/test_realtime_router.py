"""
backend/realtime/test_realtime_router.py
=========================================
Integration tests for Step 7B:
  FlowManager -> FeatureExtractor -> RealtimeDetector -> DetectionStore -> WebSocketManager -> /ws/realtime-stream

Verifies:
  1. Completed flow triggers ML detection -> DB store -> WebSocket broadcast.
  2. The SAME detection result is persisted to DB and broadcast over WebSocket.
  3. Real flow_duration_us and packet_count are accurately recorded.
  4. Raw packet payload is NEVER stored or broadcast.
  5. Error isolation: ML error, DB error, or WS error do not crash the pipeline.
  6. FastAPI WebSocket endpoint `/ws/realtime-stream` connects and receives live frames.
"""

import sys
import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.main import app
from backend.db import Base
from backend.detection.models import Detection
from backend.realtime.flow_manager import FlowManager, Flow
from backend.realtime.realtime_detector import RealtimeDetector, RealtimeDetectionResult
from backend.realtime.detection_store import store_realtime_detection
from backend.realtime.ws_manager import ws_manager, PROHIBITED_FIELDS
from backend.realtime.realtime_router import handle_completed_flow


# ---------------------------------------------------------------------------
# In-memory SQLite Database Fixture
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Isolated SQLite database session for integration tests."""
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# TEST 1: Full End-to-End Pipeline (Completed Flow -> ML -> DB -> WS)
# ---------------------------------------------------------------------------

def test_completed_flow_integrates_ml_db_and_websocket(db_session):
    """
    Verifies that a completed synthetic TCP flow is processed by ML,
    persisted into PostgreSQL (SQLite mock), and broadcast via WebSocketManager.
    """
    detector = RealtimeDetector()
    fm = FlowManager()

    # Simulate TCP handshake & payload
    fm.process_packet(
        {"src_ip": "192.168.1.150", "dst_ip": "10.0.0.1", "src_port": 54321, "dst_port": 80, "protocol": "TCP", "length": 64, "flags": {"syn": True}},
        override_time=100.0
    )
    fm.process_packet(
        {"src_ip": "10.0.0.1", "dst_ip": "192.168.1.150", "src_port": 80, "dst_port": 54321, "protocol": "TCP", "length": 64, "flags": {"syn": True, "ack": True}},
        override_time=100.02
    )
    completed_flow = fm.process_packet(
        {"src_ip": "192.168.1.150", "dst_ip": "10.0.0.1", "src_port": 54321, "dst_port": 80, "protocol": "TCP", "length": 150, "flags": {"fin": True, "ack": True}},
        override_time=100.05
    )

    assert completed_flow is not None
    assert completed_flow.packet_count == 3

    # Mock WebSocket broadcast
    broadcast_messages = []

    async def mock_broadcast(msg):
        broadcast_messages.append(msg)

    with patch.object(ws_manager, 'broadcast', side_effect=mock_broadcast):
        result = handle_completed_flow(completed_flow, detector, db=db_session)

    # 1. Check ML detection result
    assert result is not None
    assert isinstance(result, RealtimeDetectionResult)
    assert result.source_ip == "192.168.1.150"
    assert result.destination_ip == "10.0.0.1"
    assert result.source_port == 54321
    assert result.destination_port == 80
    assert result.protocol == "TCP"
    assert result.packet_count == 3
    assert result.flow_duration_us == pytest.approx(50000.0, abs=100)  # 0.05 sec = 50,000 us

    # 2. Check DB Persistence
    saved_db_row = db_session.query(Detection).filter_by(source_ip="192.168.1.150").first()
    assert saved_db_row is not None
    assert saved_db_row.destination_ip == "10.0.0.1"
    assert saved_db_row.source_port == 54321
    assert saved_db_row.destination_port == 80
    assert saved_db_row.protocol == "TCP"
    assert saved_db_row.packet_count == 3
    assert saved_db_row.flow_duration_us == pytest.approx(50000.0, abs=100)
    assert saved_db_row.prediction == result.prediction
    assert saved_db_row.risk_level == result.risk_level

    # 3. Check WebSocket Broadcast
    assert len(broadcast_messages) == 1
    ws_msg = broadcast_messages[0]
    assert ws_msg["source_ip"] == "192.168.1.150"
    assert ws_msg["destination_ip"] == "10.0.0.1"
    assert ws_msg["prediction"] == result.prediction
    assert ws_msg["confidence"] == result.confidence
    assert ws_msg["risk_level"] == result.risk_level
    assert ws_msg["flow_duration_us"] == pytest.approx(50000.0, abs=100)
    assert ws_msg["packet_count"] == 3

    # 4. Confirm NO raw packet payload anywhere
    for key in PROHIBITED_FIELDS:
        assert key not in ws_msg
        assert not hasattr(saved_db_row, key)


# ---------------------------------------------------------------------------
# TEST 2: Error Resilience (ML, DB, WS failures do not crash pipeline)
# ---------------------------------------------------------------------------

def test_ml_failure_handled_gracefully(db_session):
    """If ML inference fails, capture/pipeline must not crash."""
    detector = RealtimeDetector()
    fm = FlowManager()
    flow = fm.process_packet({"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "src_port": 100, "dst_port": 200, "protocol": "TCP", "length": 60, "flags": {"fin": True}}, override_time=1.0)
    assert flow is not None

    with patch.object(detector, "process_completed_flow", side_effect=ValueError("ML pipeline down")):
        result = handle_completed_flow(flow, detector, db=db_session)
        assert result is None  # Handled safely without raising exception


def test_db_failure_does_not_block_websocket_broadcast(db_session):
    """If DB persistence fails, WebSocket broadcast must still execute."""
    detector = RealtimeDetector()
    fm = FlowManager()
    flow = fm.process_packet({"src_ip": "10.0.0.5", "dst_ip": "10.0.0.6", "src_port": 8888, "dst_port": 80, "protocol": "TCP", "length": 100, "flags": {"fin": True}}, override_time=1.0)
    assert flow is not None

    broadcast_messages = []

    async def mock_broadcast(msg):
        broadcast_messages.append(msg)

    with patch("backend.realtime.realtime_router.store_realtime_detection", side_effect=Exception("Database lock failure")):
        with patch.object(ws_manager, 'broadcast', side_effect=mock_broadcast):
            result = handle_completed_flow(flow, detector, db=db_session)

    # ML and WS succeeded despite DB error
    assert result is not None
    assert len(broadcast_messages) == 1
    assert broadcast_messages[0]["source_ip"] == "10.0.0.5"


def test_websocket_failure_does_not_corrupt_db_store(db_session):
    """If WebSocket broadcast throws an error, DB record must still be saved."""
    detector = RealtimeDetector()
    fm = FlowManager()
    flow = fm.process_packet({"src_ip": "172.16.0.1", "dst_ip": "172.16.0.2", "src_port": 1234, "dst_port": 443, "protocol": "TCP", "length": 120, "flags": {"fin": True}}, override_time=1.0)
    assert flow is not None

    with patch.object(ws_manager, 'broadcast', side_effect=RuntimeError("WS network timeout")):
        result = handle_completed_flow(flow, detector, db=db_session)

    assert result is not None
    saved = db_session.query(Detection).filter_by(source_ip="172.16.0.1").first()
    assert saved is not None
    assert saved.destination_ip == "172.16.0.2"


# ---------------------------------------------------------------------------
# TEST 3: FastAPI WebSocket Endpoint /ws/realtime-stream
# ---------------------------------------------------------------------------

def test_fastapi_websocket_realtime_stream_endpoint():
    """Verifies that client can connect to /ws/realtime-stream and receive detection frames."""
    client = TestClient(app)

    with client.websocket_connect("/ws/realtime-stream") as websocket:
        assert ws_manager.client_count >= 1

        # Trigger a broadcast
        test_payload = ws_manager.build_detection_payload(
            prediction="DoS Hulk",
            confidence=99.1,
            attack_severity=85,
            anomaly_score=88.5,
            risk_score=92.0,
            risk_level="CRITICAL",
            source_ip="192.168.1.200",
            destination_ip="10.0.0.1",
            source_port=60000,
            destination_port=80,
            protocol="TCP",
            flow_duration_us=150000.0,
            packet_count=45,
        )

        asyncio.run(ws_manager.broadcast(test_payload))

        # Receive frame over websocket
        data = websocket.receive_json()
        assert data["prediction"] == "DoS Hulk"
        assert data["confidence"] == 99.1
        assert data["risk_level"] == "CRITICAL"
        assert data["source_ip"] == "192.168.1.200"
        assert data["destination_ip"] == "10.0.0.1"
        assert data["flow_duration_us"] == 150000.0
        assert data["packet_count"] == 45

    # After exit context, client disconnected
    assert ws_manager.client_count == 0
