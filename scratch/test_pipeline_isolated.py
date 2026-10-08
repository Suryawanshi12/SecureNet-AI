"""
Step 9 — Isolated ML/Pipeline Integration Test (no network, no DB, no WebSocket)
Tests: Flow -> FeatureExtractor -> ML -> Sanitization -> WS payload validity
"""
import sys, asyncio, json, time

# Models load automatically on import
from backend.realtime.flow_manager import Flow, FlowManager
from backend.realtime.feature_extractor import FeatureExtractor
from backend.realtime.realtime_detector import RealtimeDetector
from backend.realtime.ws_manager import ws_manager, ALLOWED_BROADCAST_FIELDS, PROHIBITED_FIELDS
from backend.detection.models import Detection

print("=" * 60)
print("SecureNet AI - Step 9: Isolated Pipeline Integration Test")
print("=" * 60)

PASS = 0
FAIL = 0

def check(label, cond, detail=""):
    global PASS, FAIL
    icon = "[PASS]" if cond else "[FAIL]"
    if cond: PASS += 1
    else: FAIL += 1
    suffix = f" ({detail})" if detail else ""
    print(f"  {icon} {label}{suffix}")
    return cond


# --- TEST 1: Flow Construction ---
print("\n[1] Flow Construction & Metadata")
t0 = time.time()
flow = Flow(
    flow_id="192.168.1.100:54321-93.184.216.34:80-6",
    source_ip="192.168.1.100",
    source_port=54321,
    destination_ip="93.184.216.34",
    destination_port=80,
    protocol="tcp",
    start_time=t0,
    last_seen=t0,
)
# Simulate 10 forward + 8 backward packets
for i in range(10):
    flow.add_packet(pkt_len=64+i*4, pkt_time=t0+i*0.01, is_forward=True,
                    flags={"syn":i==0,"ack":i>0,"fin":i==9,"psh":False,"rst":False,"urg":False,"cwe":False,"ece":False},
                    window_size=8192)
for i in range(8):
    flow.add_packet(pkt_len=128+i*8, pkt_time=t0+0.005+i*0.015, is_forward=False,
                    flags={"syn":False,"ack":True,"fin":i==7,"psh":False,"rst":False,"urg":False,"cwe":False,"ece":False},
                    window_size=8192)

check("source_ip populated", flow.source_ip == "192.168.1.100", flow.source_ip)
check("destination_ip populated", flow.destination_ip == "93.184.216.34", flow.destination_ip)
check("source_port populated", flow.source_port == 54321, str(flow.source_port))
check("destination_port populated", flow.destination_port == 80, str(flow.destination_port))
check("protocol populated", flow.protocol == "tcp", flow.protocol)
check("packet_count correct", flow.packet_count == 18, str(flow.packet_count))
check("flow duration > 0", flow.duration > 0, f"{flow.duration:.4f}s")
check("forward_packet_count == 10", flow.forward_packet_count == 10)
check("backward_packet_count == 8", flow.backward_packet_count == 8)

# --- TEST 2: Feature Extraction ---
print("\n[2] Feature Extraction (78 features)")
extractor = FeatureExtractor()
features = extractor.extract_features(flow)
check("features is dict", isinstance(features, dict))
check("exactly 78 features", len(features) == 78, f"got {len(features)}")
nan_inf_count = sum(1 for v in features.values() if v != v or v == float('inf') or v == float('-inf'))
check("no NaN or Inf values", nan_inf_count == 0, f"{nan_inf_count} bad values")
check("Flow Duration present", "Flow Duration" in features)
check("Destination Port present", "Destination Port" in features)
check("Total Fwd Packets present", "Total Fwd Packets" in features)

# --- TEST 3: RealtimeDetector (ML Inference) ---
print("\n[3] RealtimeDetector — XGBoost + IsolationForest + Risk")
detector = RealtimeDetector()
result = detector.process_completed_flow(flow)
check("result is not None", result is not None)
if result:
    check("prediction is string", isinstance(result.prediction, str), result.prediction)
    check("confidence in [0,100]", 0.0 <= result.confidence <= 100.0, f"{result.confidence:.2f}%")
    check("attack_severity in [0,100]", 0 <= result.attack_severity <= 100, str(result.attack_severity))
    check("anomaly_score in [0,100]", 0.0 <= result.anomaly_score <= 100.0, f"{result.anomaly_score:.4f}")
    check("risk_score in [0,100]", 0.0 <= result.risk_score <= 100.0, f"{result.risk_score:.2f}")
    check("risk_level valid", result.risk_level in {"LOW","MEDIUM","HIGH","CRITICAL"}, result.risk_level)
    check("source_ip preserved", result.source_ip == "192.168.1.100", result.source_ip)
    check("destination_ip preserved", result.destination_ip == "93.184.216.34", result.destination_ip)
    check("source_port preserved", result.source_port == 54321, str(result.source_port))
    check("destination_port preserved", result.destination_port == 80, str(result.destination_port))
    check("protocol preserved", result.protocol == "tcp", result.protocol)
    check("packet_count preserved", result.packet_count == 18, str(result.packet_count))
    check("flow_id present", bool(result.flow_id))
    print(f"\n     >> ML Result: prediction={result.prediction}, risk={result.risk_level} ({result.risk_score:.1f}), anomaly={result.anomaly_score:.4f}")

# --- TEST 4: WebSocket Payload Sanitization ---
print("\n[4] WebSocket Payload — Security Sanitization")
if result:
    payload = ws_manager.build_detection_payload(
        prediction=result.prediction,
        confidence=result.confidence,
        attack_severity=result.attack_severity,
        anomaly_score=result.anomaly_score,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        source_ip=result.source_ip,
        destination_ip=result.destination_ip,
        source_port=result.source_port,
        destination_port=result.destination_port,
        protocol=result.protocol,
        flow_duration_us=getattr(result, "flow_duration_us", None),
        packet_count=result.packet_count,
    )
    sanitized = ws_manager._sanitize(payload)
    check("sanitized is dict", isinstance(sanitized, dict))
    check("all fields in ALLOWED_BROADCAST_FIELDS", all(k in ALLOWED_BROADCAST_FIELDS for k in sanitized), str(set(sanitized)-ALLOWED_BROADCAST_FIELDS))
    for bad in PROHIBITED_FIELDS:
        check(f"prohibited field '{bad}' absent", bad not in sanitized)
    check("timestamp present in payload", "timestamp" in sanitized)
    check("prediction present in payload", "prediction" in sanitized)
    check("risk_level present in payload", "risk_level" in sanitized)
    check("source_ip present in payload", "source_ip" in sanitized)
    check("destination_ip present in payload", "destination_ip" in sanitized)
    check("protocol present in payload", "protocol" in sanitized)
    check("packet_count present in payload", "packet_count" in sanitized)

    # JSON-serializable
    try:
        json_str = json.dumps(sanitized, default=str)
        check("payload JSON serializable", True, f"{len(json_str)} bytes")
    except Exception as e:
        check("payload JSON serializable", False, str(e))

# --- TEST 5: Detection ORM Model Verification ---
print("\n[5] Detection ORM Model — No Raw Payload Field")
det_cols = [c.key for c in Detection.__table__.columns]
check("'payload' column NOT in Detection model", "payload" not in det_cols)
check("'prediction' column in Detection model", "prediction" in det_cols)
check("'risk_score' column in Detection model", "risk_score" in det_cols)
check("'source_ip' column in Detection model", "source_ip" in det_cols)
check("'destination_ip' column in Detection model", "destination_ip" in det_cols)
check("'source_port' column in Detection model", "source_port" in det_cols)
check("'destination_port' column in Detection model", "destination_port" in det_cols)
check("'protocol' column in Detection model", "protocol" in det_cols)
check("'packet_count' column in Detection model", "packet_count" in det_cols)
check("'flow_duration_us' column in Detection model", "flow_duration_us" in det_cols)

# --- TEST 6: FlowManager process_packet + expire_flows API ---
print("\n[6] FlowManager — process_packet (dict) + expire_flows")
fm = FlowManager(idle_timeout=0.05, active_timeout=30.0)
t_now = time.time()

# Simulate one UDP DNS packet via dict-based mock packet
fm.process_packet({
    "src_ip": "192.168.1.1", "src_port": 12345,
    "dst_ip": "8.8.8.8", "dst_port": 53,
    "protocol": "UDP", "length": 64,
    "time": t_now, "flags": {}, "window": 0
})
check("active flow created after first packet", fm.get_active_flow_count() >= 1, f"{fm.get_active_flow_count()} active")

# Expire flows by simulating future time
expired = fm.expire_flows(current_time=t_now + 2.0)
check("flow expired via idle timeout", len(expired) >= 1, f"{len(expired)} expired")
if expired:
    ef = expired[0]
    check("expired flow has source_ip", bool(ef.source_ip), ef.source_ip)
    check("expired flow has destination_ip", bool(ef.destination_ip), ef.destination_ip)
    check("expired flow packet_count >= 1", ef.packet_count >= 1, str(ef.packet_count))
    check("expired flow duration >= 0", ef.duration >= 0, f"{ef.duration:.4f}s")

# Test flush_all
fm.process_packet({
    "src_ip": "10.0.0.1", "src_port": 9999,
    "dst_ip": "1.1.1.1", "dst_port": 443,
    "protocol": "TCP", "length": 128,
    "time": t_now + 3.0, "flags": {}, "window": 8192
})
flushed = fm.flush_all()
check("flush_all clears all active flows to zero", fm.get_active_flow_count() == 0)
check("flush_all returns the flushed flows", len(flushed) >= 1, f"{len(flushed)} flushed")

# --- SUMMARY ---
print()
print("=" * 60)
print(f"ISOLATED PIPELINE TEST SUMMARY: {PASS} PASSED | {FAIL} FAILED")
print("=" * 60)
if FAIL == 0:
    print("✅ ALL checks passed — pipeline components verified.")
else:
    print(f"⚠️  {FAIL} check(s) failed — review output above.")
