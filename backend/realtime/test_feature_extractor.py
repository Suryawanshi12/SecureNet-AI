import sys
import os
import math
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.realtime.flow_manager import FlowManager, Flow
from backend.realtime.feature_extractor import FeatureExtractor
from backend.services.ml_service import EXPECTED_MODEL_FEATURES
from src.predict import predict_flow, xgb_model, anomaly_model


def create_sample_tcp_flow() -> Flow:
    """Helper to create a sample completed TCP Flow."""
    fm = FlowManager()
    # Forward packet 1
    fm.process_packet({
        "src_ip": "192.168.1.10", "dst_ip": "8.8.8.8",
        "src_port": 50000, "dst_port": 443,
        "protocol": "TCP", "length": 64,
        "flags": {"syn": True, "ack": False},
        "window": 8192
    }, override_time=100.0)

    # Backward packet 1
    fm.process_packet({
        "src_ip": "8.8.8.8", "dst_ip": "192.168.1.10",
        "src_port": 443, "dst_port": 50000,
        "protocol": "TCP", "length": 128,
        "flags": {"syn": True, "ack": True},
        "window": 8192
    }, override_time=100.05)

    # Forward packet 2 (ACK)
    fm.process_packet({
        "src_ip": "192.168.1.10", "dst_ip": "8.8.8.8",
        "src_port": 50000, "dst_port": 443,
        "protocol": "TCP", "length": 54,
        "flags": {"ack": True},
        "window": 8192
    }, override_time=100.1)

    # Forward packet 3 (PSH/ACK data)
    fm.process_packet({
        "src_ip": "192.168.1.10", "dst_ip": "8.8.8.8",
        "src_port": 50000, "dst_port": 443,
        "protocol": "TCP", "length": 320,
        "flags": {"psh": True, "ack": True},
        "window": 8192
    }, override_time=100.2)

    # Backward FIN/ACK packet (terminates flow)
    completed = fm.process_packet({
        "src_ip": "8.8.8.8", "dst_ip": "192.168.1.10",
        "src_port": 443, "dst_port": 50000,
        "protocol": "TCP", "length": 54,
        "flags": {"fin": True, "ack": True},
        "window": 8192
    }, override_time=100.3)

    return completed


def test_feature_count_and_keys():
    """Test 1: Extracted features count, key names, and order match EXPECTED_MODEL_FEATURES."""
    flow = create_sample_tcp_flow()
    features = FeatureExtractor.extract_features(flow)

    assert len(features) == 78
    assert list(features.keys()) == EXPECTED_MODEL_FEATURES


def test_no_nan_or_inf_values():
    """Test 2: All feature values are finite floats (No NaN, Inf, None, or strings)."""
    flow = create_sample_tcp_flow()
    features = FeatureExtractor.extract_features(flow)

    for k, v in features.items():
        assert isinstance(v, float), f"Feature '{k}' is not a float: {type(v)}"
        assert not math.isnan(v), f"Feature '{k}' is NaN"
        assert not math.isinf(v), f"Feature '{k}' is Inf"


def test_single_packet_flow_safety():
    """Test 3: Single-packet flow executes safely without divide-by-zero or NaNs."""
    fm = FlowManager()
    fm.process_packet({
        "src_ip": "10.0.0.1", "dst_ip": "10.0.0.2",
        "src_port": 1234, "dst_port": 80,
        "protocol": "TCP", "length": 60,
        "flags": {"syn": True}
    }, override_time=10.0)

    flushed = fm.flush_all(current_time=10.0)
    assert len(flushed) == 1

    features = FeatureExtractor.extract_features(flushed[0])
    assert len(features) == 78
    for k, v in features.items():
        assert isinstance(v, float)
        assert not math.isnan(v)
        assert not math.isinf(v)


def test_udp_flow_feature_extraction():
    """Test 4: UDP flow feature extraction works cleanly."""
    fm = FlowManager()
    fm.process_packet({
        "src_ip": "192.168.1.5", "dst_ip": "8.8.8.8",
        "src_port": 53535, "dst_port": 53,
        "protocol": "UDP", "length": 75
    }, override_time=50.0)

    fm.process_packet({
        "src_ip": "8.8.8.8", "dst_ip": "192.168.1.5",
        "src_port": 53, "dst_port": 53535,
        "protocol": "UDP", "length": 150
    }, override_time=50.05)

    flushed = fm.flush_all(current_time=50.1)
    flow = flushed[0]
    features = FeatureExtractor.extract_features(flow)

    assert features["Destination Port"] == 53.0
    assert features["Total Fwd Packets"] == 1.0
    assert features["Total Backward Packets"] == 1.0
    assert features["Total Length of Fwd Packets"] == 75.0
    assert features["Total Length of Bwd Packets"] == 150.0
    assert features["FIN Flag Count"] == 0.0


def test_xgboost_model_5_compatibility():
    """
    COMPATIBILITY TEST:
    Verifies that the generated 78-feature vector is accepted by XGBoost Model 5
    and the full predict_flow() pipeline without any modification or errors.
    """
    flow = create_sample_tcp_flow()
    features = FeatureExtractor.extract_features(flow)

    # Pass 78 extracted features directly into existing predict_flow pipeline
    result = predict_flow(features)

    assert "prediction" in result
    assert "confidence" in result
    assert "attack_severity" in result
    assert "anomaly_score" in result
    assert "risk_score" in result
    assert "risk_level" in result
    assert "explanation" in result

    # Check prediction label is one of the 15 class names
    assert result["prediction"] in [
        "BENIGN", "Bot", "DDoS", "DoS GoldenEye", "DoS Hulk", "FTP-Patator",
        "DoS slowloris", "DoS Slowhttest", "Heartbleed", "Infiltration",
        "PortScan", "SSH-Patator", "Web Attack - Brute Force",
        "Web Attack - Sql Injection", "Web Attack - XSS"
    ]
    print(f"\n[COMPATIBILITY TEST PASSED] XGBoost Prediction: {result['prediction']}, Confidence: {result['confidence']}%, Risk: {result['risk_level']}")
