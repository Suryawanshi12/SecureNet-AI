import sys
import os
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.realtime.flow_manager import FlowManager, Flow
from backend.realtime.realtime_detector import RealtimeDetector, RealtimeDetectionResult


def test_completed_tcp_flow_to_ml_prediction():
    """TEST 1: Completed TCP flow produces a valid RealtimeDetectionResult with ML metrics."""
    detector = RealtimeDetector()
    fm = FlowManager()

    # Process TCP 3-way handshake + payload + FIN
    fm.process_packet({"src_ip": "192.168.1.100", "dst_ip": "8.8.8.8", "src_port": 50000, "dst_port": 443, "protocol": "TCP", "length": 64, "flags": {"syn": True}}, override_time=1.0)
    fm.process_packet({"src_ip": "8.8.8.8", "dst_ip": "192.168.1.100", "src_port": 443, "dst_port": 50000, "protocol": "TCP", "length": 64, "flags": {"syn": True, "ack": True}}, override_time=1.05)
    fm.process_packet({"src_ip": "192.168.1.100", "dst_ip": "8.8.8.8", "src_port": 50000, "dst_port": 443, "protocol": "TCP", "length": 300, "flags": {"psh": True, "ack": True}}, override_time=1.10)
    completed_flow = fm.process_packet({"src_ip": "8.8.8.8", "dst_ip": "192.168.1.100", "src_port": 443, "dst_port": 50000, "protocol": "TCP", "length": 54, "flags": {"fin": True, "ack": True}}, override_time=1.15)

    assert completed_flow is not None

    result = detector.process_completed_flow(completed_flow)

    assert result is not None
    assert isinstance(result, RealtimeDetectionResult)
    assert result.flow_id == completed_flow.flow_id
    assert result.prediction in [
        "BENIGN", "Bot", "DDoS", "DoS GoldenEye", "DoS Hulk", "FTP-Patator",
        "DoS slowloris", "DoS Slowhttest", "Heartbleed", "Infiltration",
        "PortScan", "SSH-Patator", "Web Attack - Brute Force",
        "Web Attack - Sql Injection", "Web Attack - XSS"
    ]
    assert 0.0 <= result.confidence <= 100.0
    assert 0 <= result.attack_severity <= 100
    assert 0.0 <= result.anomaly_score <= 100.0
    assert 0.0 <= result.risk_score <= 100.0
    assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(result.explanation, list)


def test_completed_udp_flow_to_ml_prediction():
    """TEST 2: Completed UDP flow produces a valid RealtimeDetectionResult."""
    detector = RealtimeDetector()
    fm = FlowManager()

    fm.process_packet({"src_ip": "10.0.0.15", "dst_ip": "1.1.1.1", "src_port": 53535, "dst_port": 53, "protocol": "UDP", "length": 75}, override_time=10.0)
    fm.process_packet({"src_ip": "1.1.1.1", "dst_ip": "10.0.0.15", "src_port": 53, "dst_port": 53535, "protocol": "UDP", "length": 140}, override_time=10.05)

    flushed = fm.flush_all(current_time=10.1)
    assert len(flushed) == 1

    result = detector.process_completed_flow(flushed[0])
    assert result is not None
    assert result.protocol == "UDP"
    assert result.packet_count == 2
    assert result.prediction in ["BENIGN", "Bot", "DDoS", "DoS GoldenEye", "DoS Hulk", "FTP-Patator", "DoS slowloris", "DoS Slowhttest", "Heartbleed", "Infiltration", "PortScan", "SSH-Patator", "Web Attack - Brute Force", "Web Attack - Sql Injection", "Web Attack - XSS"]


def test_invalid_or_empty_flow_rejection():
    """TEST 3: Zero-packet or None flow is safely rejected without raising exceptions."""
    detector = RealtimeDetector()

    res1 = detector.process_completed_flow(None)
    assert res1 is None

    empty_flow = Flow(
        flow_id="empty-flow",
        source_ip="1.1.1.1", source_port=10,
        destination_ip="2.2.2.2", destination_port=20,
        protocol="TCP", start_time=1.0, last_seen=1.0,
        forward_packet_count=0, backward_packet_count=0
    )

    res2 = detector.process_completed_flow(empty_flow)
    assert res2 is None
    assert detector.skipped_flow_count == 2


def test_detection_callback_trigger():
    """TEST 4: Callback is invoked with RealtimeDetectionResult when flow completes."""
    received_results = []

    def my_callback(res: RealtimeDetectionResult):
        received_results.append(res)

    detector = RealtimeDetector(detection_callback=my_callback)
    fm = FlowManager()

    # Process packet 1
    fm.process_packet({"src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "src_port": 1234, "dst_port": 80, "protocol": "TCP", "length": 60, "flags": {"syn": True}}, override_time=1.0)
    flushed = fm.flush_all(current_time=2.0)

    assert len(flushed) == 1
    result = detector.process_completed_flow(flushed[0])

    assert result is not None
    assert len(received_results) == 1
    assert received_results[0].flow_id == flushed[0].flow_id
