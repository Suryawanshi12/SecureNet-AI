from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.auth.routes import router as auth_router
from backend.detection.routes import router as dashboard_router
from backend.realtime.realtime_router import router as realtime_router

from backend.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION
)

from backend.schemas import (
    PredictionRequest,
    PredictionResponse
)

from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.detection.models import Detection
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.db import get_db

from backend.services.ml_service import (
    analyze_network_flow
)


# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
       
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(realtime_router)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def root():

    return {
        "message": "SecureNet AI API is running",
        "status": "online",
        "version": APP_VERSION
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": APP_NAME
    }


# ==========================================
# MODEL INFORMATION
# ==========================================

@app.get("/model-info")
def model_info():

    return {
        "supervised_model": "XGBoost Model 5",
        "anomaly_model": "Isolation Forest V3",
        "explainability": "SHAP",
        "risk_scoring": "Risk Scoring V2",
        "classes": 15
    }


# ==========================================
# PREDICTION ENDPOINT
# ==========================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:

        result = analyze_network_flow(
            request.features
        )

        # Save detection result to PostgreSQL
        detection = Detection(
            prediction=result["prediction"],
            confidence=result["confidence"],
            attack_severity=result["attack_severity"],
            anomaly_score=result["anomaly_score"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            shap_values=result.get("explanation")
        )
        db.add(detection)
        db.commit()

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )