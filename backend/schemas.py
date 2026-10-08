from typing import Dict, List
from pydantic import BaseModel, Field


# ==========================================
# PREDICTION REQUEST
# ==========================================

class PredictionRequest(BaseModel):
    """
    Request body for network-flow prediction.

    The features dictionary should contain
    the 78 network traffic features used
    by the XGBoost model.
    """

    features: Dict[str, float] = Field(
        ...,
        description="Network flow features"
    )


# ==========================================
# SHAP EXPLANATION
# ==========================================

class SHAPExplanation(BaseModel):

    feature: str

    value: float

    shap_value: float

    direction: str


# ==========================================
# PREDICTION RESPONSE
# ==========================================

class PredictionResponse(BaseModel):

    prediction: str

    confidence: float

    attack_severity: int

    anomaly_score: float

    risk_score: float

    risk_level: str

    explanation: List[SHAPExplanation]