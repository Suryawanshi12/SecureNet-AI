"""
backend/realtime/realtime_router.py
====================================
FastAPI router and real-time pipeline orchestrator for SecureNet AI.

Connects:
  Scapy / PacketCaptureEngine
  -> FlowManager
  -> FeatureExtractor
  -> RealtimeDetector
  -> DetectionStore (PostgreSQL)
  -> WebSocketManager (Broadcast)

WebSocket Endpoints:
  - /ws/realtime-stream
  - /realtime/stream

REST Endpoints:
  - GET  /realtime/status
  - POST /realtime/start
  - POST /realtime/stop
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db import get_db, SessionLocal
from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.realtime.ws_manager import ws_manager, WebSocketManager
from backend.realtime.flow_manager import FlowManager, Flow
from backend.realtime.realtime_detector import RealtimeDetector, RealtimeDetectionResult
from backend.realtime.detection_store import store_realtime_detection
from backend.realtime.packet_capture import PacketCaptureEngine

logger = logging.getLogger("RealtimeRouter")

router = APIRouter(tags=["Realtime Monitoring"])


# ---------------------------------------------------------------------------
# Core Pipeline Callback Handler
# ---------------------------------------------------------------------------

def handle_completed_flow(
    flow: Flow,
    detector: RealtimeDetector,
    db: Optional[Session] = None,
    event_loop: Optional[asyncio.AbstractEventLoop] = None
) -> Optional[RealtimeDetectionResult]:
    """
    Orchestrates processing for a completed network flow across ML, DB, and WS.

    Guarantees:
      - ML failure does NOT crash capture.
      - DB failure does NOT crash capture or WebSocket broadcast.
      - WebSocket failure does NOT crash detection or DB storage.
      - Raw packet payload is NEVER stored or transmitted.
    """
    # 1. Generate ML Prediction & Explanation
    try:
        result = detector.process_completed_flow(flow)
    except Exception as exc:
        logger.error(f"ML detection failed for flow '{getattr(flow, 'flow_id', 'unknown')}': {exc}")
        return None

    if result is None:
        return None

    # 2. Persist Detection to PostgreSQL via DetectionStore
    try:
        store_realtime_detection(result, db=db)
    except Exception as exc:
        logger.error(f"DB persistence failed for flow '{result.flow_id}': {exc}")

    # 3. Broadcast SAME detection result to connected clients via WebSocketManager
    try:
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
            shap_values=result.explanation,
        )

        _schedule_broadcast(payload, event_loop=event_loop)
    except Exception as exc:
        logger.error(f"WebSocket broadcast preparation failed for flow '{result.flow_id}': {exc}")

    return result


def _schedule_broadcast(payload: Dict[str, Any], event_loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """
    Safely schedules ws_manager.broadcast(payload) whether called from sync thread or async event loop.
    """
    try:
        target_loop = event_loop
        if target_loop is None or not target_loop.is_running():
            try:
                target_loop = asyncio.get_running_loop()
            except RuntimeError:
                try:
                    target_loop = asyncio.get_event_loop()
                except RuntimeError:
                    target_loop = None

        if target_loop is not None and target_loop.is_running():
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), target_loop)
        else:
            # Fallback for synchronous execution (e.g., unit test environments)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), loop)
                else:
                    loop.run_until_complete(ws_manager.broadcast(payload))
            except Exception:
                asyncio.run(ws_manager.broadcast(payload))
    except Exception as exc:
        logger.error(f"Failed to schedule WebSocket broadcast: {exc}")


# ---------------------------------------------------------------------------
# Global Pipeline State (Live Packet Capture Control)
# ---------------------------------------------------------------------------

class PipelineState:
    def __init__(self):
        self.is_running = False
        self.capture_engine: Optional[PacketCaptureEngine] = None
        self.flow_manager: Optional[FlowManager] = None
        self.detector: Optional[RealtimeDetector] = None
        self.capture_thread: Optional[threading.Thread] = None

pipeline_state = PipelineState()


# ---------------------------------------------------------------------------
# WebSocket Endpoints
# ---------------------------------------------------------------------------

@router.websocket("/ws/realtime-stream")
async def realtime_stream_ws(websocket: WebSocket):
    """
    Real-Time WebSocket Detection Stream Endpoint.

    Connects frontend client to WebSocketManager to receive live ML detection JSON frames.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open; receive optional ping messages from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.warning(f"WebSocket client disconnected: {exc}")
        ws_manager.disconnect(websocket)


@router.websocket("/realtime/stream")
async def realtime_stream_ws_alias(websocket: WebSocket):
    """Alias for /ws/realtime-stream."""
    await realtime_stream_ws(websocket)


# ---------------------------------------------------------------------------
# REST Endpoints for Capture Control & Status
# ---------------------------------------------------------------------------

@router.get("/realtime/status")
def get_realtime_status():
    """Returns operational status of the real-time pipeline."""
    return {
        "status": "running" if pipeline_state.is_running else "stopped",
        "active_ws_clients": ws_manager.client_count,
        "processed_flows": pipeline_state.detector.processed_flow_count if pipeline_state.detector else 0,
        "skipped_flows": pipeline_state.detector.skipped_flow_count if pipeline_state.detector else 0,
    }


@router.post("/realtime/start")
def start_realtime_pipeline(
    interface: Optional[str] = None,
    bpf_filter: Optional[str] = "ip",
    current_user: User = Depends(get_current_user)
):
    """Starts live packet capture & detection pipeline in a background thread."""
    if pipeline_state.is_running:
        return {"message": "Real-time pipeline is already running.", "status": "running"}

    detector = RealtimeDetector()
    
    def on_flow_complete(flow: Flow):
        handle_completed_flow(flow, detector, event_loop=None)

    flow_manager = FlowManager()
    capture_engine = PacketCaptureEngine(
        flow_manager=flow_manager,
        interface=interface,
        bpf_filter=bpf_filter,
        flow_callback=on_flow_complete
    )

    def capture_worker():
        try:
            capture_engine.start()
        except Exception as exc:
            logger.error(f"Error in capture worker thread: {exc}")
        finally:
            pipeline_state.is_running = False

    thread = threading.Thread(target=capture_worker, daemon=True)
    pipeline_state.is_running = True
    pipeline_state.capture_engine = capture_engine
    pipeline_state.flow_manager = flow_manager
    pipeline_state.detector = detector
    pipeline_state.capture_thread = thread
    thread.start()

    return {"message": "Real-time pipeline started successfully.", "status": "running"}


@router.post("/realtime/stop")
def stop_realtime_pipeline(current_user: User = Depends(get_current_user)):
    """Stops the live packet capture & detection pipeline."""
    if not pipeline_state.is_running or not pipeline_state.capture_engine:
        return {"message": "Real-time pipeline is not running.", "status": "stopped"}

    pipeline_state.capture_engine.stop()
    pipeline_state.is_running = False

    return {"message": "Real-time pipeline stopped successfully.", "status": "stopped"}
