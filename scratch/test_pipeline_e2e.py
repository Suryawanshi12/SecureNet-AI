import asyncio
import json
import logging
from sqlalchemy import create_engine, text
from backend.db import SessionLocal, engine
from backend.detection.models import Detection
from backend.realtime.realtime_detector import RealtimeDetector
from backend.realtime.flow_manager import Flow
from backend.realtime.detection_store import store_realtime_detection
from backend.realtime.ws_manager import ws_manager, WebSocketManager
from backend.realtime.packet_capture import PacketCaptureEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2E_Test")

def test_postgresql_connection():
    print("\n--- 1. Testing PostgreSQL Database Connection ---")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM detections;")).fetchone()
            count = result[0] if result else 0
            print(f"✅ PostgreSQL connection SUCCESSFUL! Existing detections count: {count}")
            return True, count
    except Exception as e:
        print(f"❌ PostgreSQL connection FAILED: {e}")
        return False, 0

def test_scapy_npcap_permissions():
    print("\n--- 2. Testing Scapy / Npcap Live Packet Capture Capabilities ---")
    try:
        from scapy.all import sniff
        print("Attempting 2-second packet sniff on default interface...")
        packets = sniff(count=5, timeout=2)
        print(f"✅ Packet capture SUCCESSFUL! Captured {len(packets)} live packets.")
        return True, len(packets)
    except Exception as e:
        print(f"⚠️ Live Packet capture note/limitation: {e}")
        print("Note: Live raw packet capture on Windows requires Npcap driver and Administrator execution privileges.")
        return False, 0

async def test_full_pipeline_simulation():
    print("\n--- 3. Testing Full Pipeline Integration (Flow -> ML -> DB -> WebSocket) ---")
    detector = RealtimeDetector()
    
    # Create a dummy flow mimicking a completed TCP HTTP flow
    flow = Flow(
        flow_id="192.168.1.100:54321-93.184.216.34:80-6",
        src_ip="192.168.1.100",
        src_port=54321,
        dst_ip="93.184.216.34",
        dst_port=80,
        protocol="tcp"
    )
    # Add dummy packets to calculate duration and packet count
    flow.update("192.168.1.100", 54321, "93.184.216.34", 80, "tcp", 64, 0.0)
    flow.update("93.184.216.34", 80, "192.168.1.100", 54321, "tcp", 128, 0.05)
    
    # 1. Process flow through RealtimeDetector
    detection_res = detector.process_completed_flow(flow)
    if not detection_res:
        print("❌ ML RealtimeDetector failed to process flow.")
        return False
    
    print(f"  [ML] Prediction: {detection_res.prediction} | Confidence: {detection_res.confidence:.2f}% | Risk: {detection_res.risk_level} ({detection_res.risk_score:.2f}) | Anomaly Score: {detection_res.anomaly_score:.4f}")
    
    # 2. Persist to DB
    db_obj = store_realtime_detection(detection_res)
    if not db_obj:
        print("❌ PostgreSQL store_realtime_detection failed.")
        return False
    print(f"  [DB] Stored record ID #{db_obj.id} in PostgreSQL detections table.")

    # 3. Construct WebSocket broadcast payload
    ws_payload = ws_manager.build_detection_payload(
        prediction=detection_res.prediction,
        confidence=detection_res.confidence,
        attack_severity=detection_res.attack_severity,
        anomaly_score=detection_res.anomaly_score,
        risk_score=detection_res.risk_score,
        risk_level=detection_res.risk_level,
        source_ip=detection_res.source_ip,
        destination_ip=detection_res.destination_ip,
        source_port=detection_res.source_port,
        destination_port=detection_res.destination_port,
        protocol=detection_res.protocol,
        flow_duration_us=getattr(detection_res, "flow_duration_us", None),
        packet_count=detection_res.packet_count,
    )
    
    sanitized = ws_manager._sanitize(ws_payload)
    print(f"  [WS] Sanitized payload ready for broadcast (fields: {list(sanitized.keys())})")
    
    # Verify no raw payload, token or credential present
    for bad in ["payload", "content", "packet_data", "password", "token", "jwt"]:
        if bad in sanitized:
            print(f"❌ Security failure: prohibited field '{bad}' found in broadcast!")
            return False
            
    print("✅ Full pipeline simulation (Flow -> ML -> DB -> WS payload) PASSED cleanly!")
    return True

if __name__ == "__main__":
    db_ok, count = test_postgresql_connection()
    sniff_ok, pkts = test_scapy_npcap_permissions()
    pipeline_ok = asyncio.run(test_full_pipeline_simulation())
    print("\nSummary:")
    print(f"PostgreSQL DB: {'OK' if db_ok else 'FAIL'}")
    print(f"Live Scapy Sniff: {'OK' if sniff_ok else 'ADMIN/NPCAP REQUIRED'}")
    print(f"Full Pipeline Integration: {'OK' if pipeline_ok else 'FAIL'}")
