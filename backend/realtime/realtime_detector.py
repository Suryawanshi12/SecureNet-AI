import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Dict, Any

from backend.realtime.flow_manager import Flow
from backend.realtime.feature_extractor import FeatureExtractor
from backend.services.ml_service import analyze_network_flow, EXPECTED_MODEL_FEATURES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("RealtimeDetector")


@dataclass
class RealtimeDetectionResult:
    """
    Structured Real-Time Detection Result.
    Encapsulates network flow metadata with ML prediction, risk scoring, and SHAP explainability.
    """
    flow_id: str
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int
    protocol: str
    packet_count: int
    total_bytes: int
    prediction: str
    confidence: float
    attack_severity: int
    anomaly_score: float
    risk_score: float
    risk_level: str
    explanation: List[Dict[str, Any]] = field(default_factory=list)
    flow_duration_us: Optional[float] = None


class RealtimeDetector:
    """
    Real-Time ML Intrusion & Anomaly Detection Coordinator.

    Processes completed/expired Flow objects from FlowManager, extracts 78 features,
    validates feature structure, passes features to analyze_network_flow(),
    and triggers downstream notification callbacks.
    """

    def __init__(
        self,
        detection_callback: Optional[Callable[[RealtimeDetectionResult], None]] = None,
        enable_ml: bool = True
    ):
        self.detection_callback = detection_callback
        self.enable_ml = enable_ml
        self.detection_results: List[RealtimeDetectionResult] = []
        self.processed_flow_count = 0
        self.skipped_flow_count = 0

    def process_completed_flow(self, flow: Optional[Flow]) -> Optional[RealtimeDetectionResult]:
        """
        Callback handler for completed or expired Flow instances.

        Extracts 78 features, validates completeness, executes ML inference,
        and constructs a RealtimeDetectionResult.
        """
        self.processed_flow_count += 1

        # Safe guard against invalid or empty flow objects
        if not flow or flow.packet_count == 0:
            logger.warning(
                f"Skipping ML prediction for flow "
                f"'{flow.flow_id if flow else 'None'}': Flow has zero packets or is invalid."
            )
            self.skipped_flow_count += 1
            return None

        # 1. Feature Extraction
        try:
            features = FeatureExtractor.extract_features(flow)
        except Exception as e:
            logger.error(f"Failed to extract features for flow '{flow.flow_id}': {e}")
            self.skipped_flow_count += 1
            return None

        # 2. Validation of 78 feature count and order
        if not features or len(features) != len(EXPECTED_MODEL_FEATURES):
            logger.warning(
                f"Skipping flow '{flow.flow_id}': Feature count mismatch "
                f"(expected {len(EXPECTED_MODEL_FEATURES)}, got {len(features) if features else 0})."
            )
            self.skipped_flow_count += 1
            return None

        if not self.enable_ml:
            return None

        # 3. ML Pipeline Inference (XGBoost, Isolation Forest, SHAP, Risk Scoring)
        try:
            ml_result = analyze_network_flow(features)
        except Exception as e:
            logger.error(f"ML prediction pipeline error for flow '{flow.flow_id}': {e}")
            self.skipped_flow_count += 1
            return None

        # 4. Construct Structured Detection Result
        result = RealtimeDetectionResult(
            flow_id=flow.flow_id,
            source_ip=flow.source_ip,
            source_port=flow.source_port,
            destination_ip=flow.destination_ip,
            destination_port=flow.destination_port,
            protocol=flow.protocol,
            packet_count=flow.packet_count,
            total_bytes=flow.total_bytes,
            flow_duration_us=round(flow.duration * 1_000_000.0, 2),
            prediction=ml_result["prediction"],
            confidence=ml_result["confidence"],
            attack_severity=ml_result["attack_severity"],
            anomaly_score=ml_result["anomaly_score"],
            risk_score=ml_result["risk_score"],
            risk_level=ml_result["risk_level"],
            explanation=ml_result.get("explanation", []),
        )

        self.detection_results.append(result)

        logger.info(
            f"REALTIME ML DETECTION [{result.flow_id}]: "
            f"Prediction={result.prediction}, Confidence={result.confidence}%, "
            f"AnomalyScore={result.anomaly_score}, RiskScore={result.risk_score} ({result.risk_level})"
        )

        if self.detection_callback:
            try:
                self.detection_callback(result)
            except Exception as e:
                logger.error(f"Error in detection_callback: {e}")

        return result
