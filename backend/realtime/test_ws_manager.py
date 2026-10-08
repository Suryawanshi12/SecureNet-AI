"""
backend/realtime/test_ws_manager.py
=====================================
Unit tests for WebSocketManager using mocked WebSocket objects.
No live network connections are required.

Tests:
  1.  Client can connect
  2.  Client can disconnect
  3.  Single client receives broadcast
  4.  Multiple clients receive broadcast
  5.  Disconnected client is removed safely
  6.  Failed client does not crash entire broadcast
  7.  Broadcast message contains only allowed detection metadata
  8.  Prohibited fields (payload/raw/token) are stripped from broadcast
  9.  Empty client list is handled safely (no-op)
  10. build_detection_payload produces only allowed fields
  11. _sanitize adds timestamp if missing
  12. Duplicate connect does not register client twice
"""

import asyncio
import json
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from unittest.mock import AsyncMock, MagicMock, patch
from backend.realtime.ws_manager import (
    WebSocketManager,
    ALLOWED_BROADCAST_FIELDS,
    PROHIBITED_FIELDS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_ws(fail_on_send: bool = False) -> MagicMock:
    """Create a mock WebSocket with accept() and send_text() as AsyncMocks."""
    ws = MagicMock()
    ws.accept = AsyncMock()
    if fail_on_send:
        ws.send_text = AsyncMock(side_effect=RuntimeError("Client gone"))
    else:
        ws.send_text = AsyncMock()
    return ws


def run(coro):
    """Run an async coroutine synchronously in tests."""
    return asyncio.run(coro)


def _sample_message() -> dict:
    return {
        "timestamp": "2026-10-06T19:00:00+00:00",
        "prediction": "DDoS",
        "confidence": 98.7,
        "attack_severity": 80,
        "anomaly_score": 72.3,
        "risk_score": 85.0,
        "risk_level": "CRITICAL",
        "source_ip": "10.0.0.1",
        "destination_ip": "192.168.1.1",
        "source_port": 54321,
        "destination_port": 80,
        "protocol": "TCP",
        "flow_duration_us": 120000.0,
        "packet_count": 500,
    }


# ---------------------------------------------------------------------------
# TEST 1: Client can connect
# ---------------------------------------------------------------------------

def test_client_can_connect():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))

    assert manager.client_count == 1
    ws.accept.assert_called_once()


# ---------------------------------------------------------------------------
# TEST 2: Client can disconnect
# ---------------------------------------------------------------------------

def test_client_can_disconnect():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))
    manager.disconnect(ws)

    assert manager.client_count == 0


# ---------------------------------------------------------------------------
# TEST 3: Single client receives broadcast
# ---------------------------------------------------------------------------

def test_single_client_receives_broadcast():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))
    run(manager.broadcast(_sample_message()))

    ws.send_text.assert_called_once()
    payload = json.loads(ws.send_text.call_args[0][0])
    assert payload["prediction"] == "DDoS"
    assert payload["risk_level"] == "CRITICAL"


# ---------------------------------------------------------------------------
# TEST 4: Multiple clients receive broadcast
# ---------------------------------------------------------------------------

def test_multiple_clients_receive_broadcast():
    manager = WebSocketManager()
    clients = [make_mock_ws() for _ in range(5)]
    for ws in clients:
        run(manager.connect(ws))

    assert manager.client_count == 5
    run(manager.broadcast(_sample_message()))

    for ws in clients:
        ws.send_text.assert_called_once()


# ---------------------------------------------------------------------------
# TEST 5: Disconnected client is removed safely
# ---------------------------------------------------------------------------

def test_disconnected_client_removed_safely():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))
    manager.disconnect(ws)

    # Disconnecting again must not raise
    manager.disconnect(ws)
    assert manager.client_count == 0


# ---------------------------------------------------------------------------
# TEST 6: Failed client does not crash the entire broadcast
# ---------------------------------------------------------------------------

def test_failed_client_does_not_crash_broadcast():
    manager = WebSocketManager()
    good_ws = make_mock_ws()
    bad_ws = make_mock_ws(fail_on_send=True)

    run(manager.connect(good_ws))
    run(manager.connect(bad_ws))

    assert manager.client_count == 2

    # Broadcast must not raise even though bad_ws fails
    run(manager.broadcast(_sample_message()))

    # Good client still received the message
    good_ws.send_text.assert_called_once()

    # Bad client was removed from the pool
    assert manager.client_count == 1
    assert bad_ws not in manager._clients


# ---------------------------------------------------------------------------
# TEST 7: Broadcast message contains only allowed detection metadata
# ---------------------------------------------------------------------------

def test_broadcast_contains_only_allowed_fields():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))
    run(manager.broadcast(_sample_message()))

    payload = json.loads(ws.send_text.call_args[0][0])
    for key in payload:
        assert key in ALLOWED_BROADCAST_FIELDS, (
            f"Unexpected field '{key}' found in broadcast payload."
        )


# ---------------------------------------------------------------------------
# TEST 8: Prohibited fields are stripped from broadcast
# ---------------------------------------------------------------------------

def test_prohibited_fields_stripped_from_broadcast():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))

    dirty_message = dict(_sample_message())
    dirty_message["payload"] = b"SENSITIVE RAW PACKET BYTES"
    dirty_message["token"] = "eyJhbGciOiJIUzI1NiJ9..."
    dirty_message["password"] = "hunter2"
    dirty_message["raw"] = "0x0800deadbeef"

    run(manager.broadcast(dirty_message))

    payload = json.loads(ws.send_text.call_args[0][0])
    for prohibited in PROHIBITED_FIELDS:
        assert prohibited not in payload, (
            f"Prohibited field '{prohibited}' was transmitted in broadcast!"
        )


# ---------------------------------------------------------------------------
# TEST 9: Empty client list is handled safely
# ---------------------------------------------------------------------------

def test_empty_client_list_broadcast_is_safe():
    manager = WebSocketManager()
    # Must not raise with zero clients
    run(manager.broadcast(_sample_message()))
    assert manager.client_count == 0


# ---------------------------------------------------------------------------
# TEST 10: build_detection_payload produces only allowed fields
# ---------------------------------------------------------------------------

def test_build_detection_payload_allowed_fields_only():
    payload = WebSocketManager.build_detection_payload(
        prediction="PortScan",
        confidence=91.5,
        attack_severity=40,
        anomaly_score=30.0,
        risk_score=45.0,
        risk_level="MEDIUM",
        source_ip="172.16.0.5",
        destination_ip="10.10.10.1",
        source_port=12345,
        destination_port=22,
        protocol="TCP",
        flow_duration_us=50000.0,
        packet_count=12,
    )
    for key in payload:
        assert key in ALLOWED_BROADCAST_FIELDS, (
            f"build_detection_payload produced disallowed field: '{key}'"
        )
    for prohibited in PROHIBITED_FIELDS:
        assert prohibited not in payload


# ---------------------------------------------------------------------------
# TEST 11: _sanitize adds timestamp if missing
# ---------------------------------------------------------------------------

def test_sanitize_adds_timestamp_if_missing():
    msg = {
        "prediction": "BENIGN",
        "confidence": 99.0,
        "attack_severity": 0,
        "anomaly_score": 0.0,
        "risk_score": 1.0,
        "risk_level": "LOW",
    }
    sanitized = WebSocketManager._sanitize(msg)
    assert "timestamp" in sanitized
    assert sanitized["timestamp"]  # non-empty


# ---------------------------------------------------------------------------
# TEST 12: Duplicate connect does not register client twice
# ---------------------------------------------------------------------------

def test_duplicate_connect_not_registered_twice():
    manager = WebSocketManager()
    ws = make_mock_ws()
    run(manager.connect(ws))
    run(manager.connect(ws))  # second call with same object

    assert manager.client_count == 1
