from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func

from backend.db import Base


class Detection(Base):
    __tablename__ = "detections"

    # ── Core detection fields (used by both /predict and real-time pipeline) ──
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    prediction = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    attack_severity = Column(Integer, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    shap_values = Column(JSON, nullable=True)

    # ── Real-time flow metadata (nullable – not populated by /predict endpoint) ──
    # Raw packet payload is NEVER stored here.
    source_ip = Column(String(45), nullable=True, index=True)       # IPv4 / IPv6
    destination_ip = Column(String(45), nullable=True, index=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(10), nullable=True)                    # TCP / UDP
    flow_duration_us = Column(Float, nullable=True)                 # microseconds
    packet_count = Column(Integer, nullable=True)
