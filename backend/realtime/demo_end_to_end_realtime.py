import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from scapy.layers.inet import IP, TCP
from backend.realtime.flow_manager import FlowManager
from backend.realtime.feature_extractor import FeatureExtractor
from backend.realtime.realtime_detector import RealtimeDetector, RealtimeDetectionResult


def run_manual_test():
    print("==================================================")
    print("SECURENET AI REALTIME PIPELINE MANUAL DEMO")
    print("Flow -> 78 Features -> XGBoost Prediction -> Risk Level")
    print("==================================================")

    # 1. Initialize RealtimeDetector and FlowManager
    detections = []
    detector = RealtimeDetector(detection_callback=lambda res: detections.append(res))
    fm = FlowManager()

    # 2. Simulate raw network packet stream for a flow (A -> B traffic)
    print("\n[STEP 1] Simulating incoming raw packet stream...")

    pkt1 = IP(src="192.168.1.100", dst="172.217.14.206") / TCP(sport=54321, dport=443, flags="S")
    pkt2 = IP(src="172.217.14.206", dst="192.168.1.100") / TCP(sport=443, dport=54321, flags="SA")
    pkt3 = IP(src="192.168.1.100", dst="172.217.14.206") / TCP(sport=54321, dport=443, flags="PA") / (b"X" * 450)
    pkt4 = IP(src="172.217.14.206", dst="192.168.1.100") / TCP(sport=443, dport=54321, flags="FA")

    # Feed packets to FlowManager
    fm.process_packet(pkt1, override_time=100.0)
    fm.process_packet(pkt2, override_time=100.02)
    fm.process_packet(pkt3, override_time=100.05)
    completed_flow = fm.process_packet(pkt4, override_time=100.10)

    print(f"Flow Completed: {completed_flow.flow_id}")
    print(f"Packets: {completed_flow.packet_count} (Fwd: {completed_flow.forward_packet_count}, Bwd: {completed_flow.backward_packet_count})")
    print(f"Duration: {completed_flow.duration * 1000:.2f} ms")

    # 3. Extract 78 features
    print("\n[STEP 2] Extracting 78 CICIDS2017 features...")
    features = FeatureExtractor.extract_features(completed_flow)
    print(f"Extracted feature count: {len(features)}")
    print(f"Sample Features: Flow Duration={features['Flow Duration']}us, Fwd Packets={features['Total Fwd Packets']}, Destination Port={features['Destination Port']}")

    # 4. Run ML Inference through RealtimeDetector
    print("\n[STEP 3] Running XGBoost + Isolation Forest + SHAP ML Pipeline...")
    result = detector.process_completed_flow(completed_flow)

    # 5. Display End-to-End Prediction Summary
    print("\n==================================================")
    print("PIPELINE DEMO RESULT SUMMARY")
    print("==================================================")
    print(f"Flow ID:          {result.flow_id}")
    print(f"Prediction:       {result.prediction}")
    print(f"Confidence:       {result.confidence}%")
    print(f"Attack Severity:  {result.attack_severity}")
    print(f"Anomaly Score:    {result.anomaly_score}")
    print(f"Risk Score:       {result.risk_score}")
    print(f"Risk Level:       {result.risk_level}")
    print(f"SHAP Top Feature: {result.explanation[0]['feature']} ({result.explanation[0]['direction']})")
    print("==================================================")
    print("MANUAL PIPELINE DEMO COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_manual_test()
