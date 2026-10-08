"""
backend/realtime/ws_manager.py
================================
WebSocket connection manager for SecureNet AI real-time detection streaming.

Responsibilities:
    - Track all connected WebSocket clients.
    - Broadcast real-time detection metadata to every connected client.
    - Remove clients that disconnect or fail during broadcast.
    - Never store raw packet payloads, JWT tokens, or credentials.
    - Never perform ML inference or DB access.

This module is intentionally narrow in scope — it is ONLY responsible
for the WebSocket communication layer.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger("WebSocketManager")


# ---------------------------------------------------------------------------
# Allowed broadcast field names (whitelist)
# Raw packet content, passwords, and credentials are explicitly excluded.
# ---------------------------------------------------------------------------

ALLOWED_BROADCAST_FIELDS: Set[str] = {
    "timestamp",
    "prediction",
    "confidence",
    "attack_severity",
    "anomaly_score",
    "risk_score",
    "risk_level",
    "source_ip",
    "destination_ip",
    "source_port",
    "destination_port",
    "protocol",
    "flow_duration_us",
    "packet_count",
    "shap_values",
}

# Fields that must NEVER appear in a broadcast message.
PROHIBITED_FIELDS: Set[str] = {
    "payload",
    "content",
    "packet_data",
    "raw",
    "body",
    "data",
    "password",
    "token",
    "jwt",
    "secret",
    "credential",
}


class WebSocketManager:
    """
    Manages WebSocket client connections and broadcasts detection events.

    Usage::

        manager = WebSocketManager()

        # In a FastAPI WebSocket endpoint:
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()   # keep-alive
        except WebSocketDisconnect:
            manager.disconnect(websocket)

        # From the real-time detection pipeline callback:
        await manager.broadcast(detection_payload)
    """

    def __init__(self) -> None:
        # Use a list so broadcast iteration order is stable.
        self._clients: List[WebSocket] = []

    # ------------------------------------------------------------------ #
    # Connection management                                                #
    # ------------------------------------------------------------------ #

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket client.

        Args:
            websocket: An incoming FastAPI WebSocket connection.
        """
        await websocket.accept()
        if websocket not in self._clients:
            self._clients.append(websocket)
            logger.info(
                f"Client connected. Total connected: {len(self._clients)}"
            )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket client from the active pool.

        Safe to call even if the client is not currently registered
        (e.g., already removed by a failed broadcast).

        Args:
            websocket: The WebSocket connection to remove.
        """
        if websocket in self._clients:
            self._clients.remove(websocket)
            logger.info(
                f"Client disconnected. Remaining connected: {len(self._clients)}"
            )

    @property
    def client_count(self) -> int:
        """Returns the number of currently connected clients."""
        return len(self._clients)

    # ------------------------------------------------------------------ #
    # Broadcasting                                                         #
    # ------------------------------------------------------------------ #

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a detection event to all connected WebSocket clients.

        - Only fields in ALLOWED_BROADCAST_FIELDS are transmitted.
        - Any PROHIBITED_FIELDS present in the message are stripped and logged.
        - Clients that fail to receive the message are disconnected gracefully;
          a single failing client never interrupts broadcast to other clients.
        - An empty client list is handled safely (no-op).

        Args:
            message: A dict containing real-time detection metadata.
                     Raw packet payloads must NEVER be included.
        """
        if not self._clients:
            logger.debug("broadcast: no connected clients — skipping.")
            return

        sanitized = self._sanitize(message)
        payload_text = json.dumps(sanitized, default=str)

        # Iterate over a snapshot so mid-loop removals are safe.
        failed: List[WebSocket] = []
        for client in list(self._clients):
            try:
                await client.send_text(payload_text)
            except Exception as exc:
                logger.warning(
                    f"Failed to send to client; removing from pool. Reason: {exc}"
                )
                failed.append(client)

        for client in failed:
            self.disconnect(client)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sanitize(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strip prohibited fields and retain only allowed detection metadata.

        Adds a UTC timestamp if one is not already present.

        Args:
            message: Raw detection dict from the pipeline.

        Returns:
            Cleaned dict safe to transmit to frontend clients.
        """
        # Remove prohibited fields first
        found_prohibited = PROHIBITED_FIELDS & set(message.keys())
        if found_prohibited:
            logger.warning(
                f"_sanitize: removing prohibited field(s) from broadcast: "
                f"{found_prohibited}"
            )

        # Keep only allowed fields
        sanitized: Dict[str, Any] = {
            k: v for k, v in message.items()
            if k in ALLOWED_BROADCAST_FIELDS
        }

        # Guarantee a timestamp is always present
        if "timestamp" not in sanitized:
            sanitized["timestamp"] = datetime.now(timezone.utc).isoformat()

        return sanitized

    @staticmethod
    def build_detection_payload(
        prediction: str,
        confidence: float,
        attack_severity: int,
        anomaly_score: float,
        risk_score: float,
        risk_level: str,
        source_ip: Optional[str] = None,
        destination_ip: Optional[str] = None,
        source_port: Optional[int] = None,
        destination_port: Optional[int] = None,
        protocol: Optional[str] = None,
        flow_duration_us: Optional[float] = None,
        packet_count: Optional[int] = None,
        shap_values: Optional[Any] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Construct a well-typed detection broadcast payload.

        Use this factory method to ensure only allowed fields are included
        when building messages programmatically from RealtimeDetectionResult.

        Returns:
            A dict ready to pass to ``WebSocketManager.broadcast()``.
        """
        return {
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "prediction": prediction,
            "confidence": confidence,
            "attack_severity": attack_severity,
            "anomaly_score": anomaly_score,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "source_port": source_port,
            "destination_port": destination_port,
            "protocol": protocol,
            "flow_duration_us": flow_duration_us,
            "packet_count": packet_count,
            "shap_values": shap_values,
        }


# ---------------------------------------------------------------------------
# Global singleton — imported by the FastAPI router in the next step.
# ---------------------------------------------------------------------------

ws_manager = WebSocketManager()
