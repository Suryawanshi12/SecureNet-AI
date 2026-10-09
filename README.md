# 🛡️ SecureNet AI

> **Next-Generation Real-Time AI Network Intrusion Detection & Explainable Threat Monitoring System**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost_v5-EB5424?style=flat-square&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SHAP](https://img.shields.io/badge/Explainability-SHAP-FF6F00?style=flat-square)](https://shap.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Machine Learning & Threat Classification](#-machine-learning--threat-classification)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [1. Database Setup (PostgreSQL)](#1-database-setup-postgresql)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Security & Compliance](#-security--compliance)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Overview

**SecureNet AI** is an enterprise-grade Network Intrusion Detection System (NIDS) designed to protect modern network infrastructure. By integrating **supervised multi-class gradient boosting (XGBoost)**, **unsupervised anomaly detection (Isolation Forest)**, and **explainable AI (SHAP)** with a **real-time live packet sniffer engine**, SecureNet AI detects both known attack vectors and zero-day anomalies at line rate, complete with human-interpretable root-cause explanations and dynamic risk assessment.

---

## ✨ Key Features

### 🔍 Dual-Engine Threat Detection
- **Multi-Class Classifier (XGBoost v5):** Classifies traffic across 15 distinct network behavior classes (14 attack categories + BENIGN).
- **Zero-Day Anomaly Detection (Isolation Forest v3):** Identifies novel/unknown anomalies and traffic deviations using unsupervised scoring.
- **Dynamic Composite Risk Scoring:** Aggregates classification confidence, attack severity weights, and anomaly scores into a standardized risk index (`0 - 100`) and categorical severity level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### 💡 Explainable AI (XAI) with SHAP
- Instant feature-attribution breakdowns via `shap.TreeExplainer`.
- Exposes the top contributing flow features and their directional impact (e.g., increased flow duration, anomalous packet sizes, TCP flag irregularities) for every flagged intrusion.

### ⚡ Real-Time Live Traffic Sniffer & Streaming
- Live network packet capture powered by **Scapy**.
- Bidirectional TCP/UDP stateful flow aggregation with idle/active timeout management.
- Real-time 78-dimension feature extraction compatible with the CIC-IDS2017 feature specification.
- Sub-second threat alert streaming to the dashboard via **WebSockets** (`/ws/realtime`).

### 🔐 Secure Authentication & Access Control
- Full JWT authentication flow with role-based access control.
- Modern password hashing powered by **Argon2** via `pwdlib`.
- Rate limiting and protected API & WebSocket endpoints.

### 📊 Modern Cyber Command Center UI
- Glassmorphism dark-mode interface built with React, Vite, and Lucide icons.
- Real-time threat log feed, live throughput charts, multi-class distribution graphs, and granular detection inspection modal.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Network Layer
        NET[Network Interface / Raw Packets]
    end

    subgraph Real-Time Ingestion Engine
        PCAP[Scapy Packet Sniffer]
        FM[Stateful Flow Manager]
        FE[78-Feature Extractor]
    end

    subgraph AI Inference Pipeline
        XGB[XGBoost Classifier v5]
        IF[Isolation Forest v3]
        SHAP[SHAP TreeExplainer]
        RISK[Risk Scoring Engine]
    end

    subgraph Storage & Communication
        PG[(PostgreSQL Database)]
        WS[WebSocket Manager]
        API[FastAPI Backend]
    end

    subgraph Client Application
        UI[React Dashboard]
    end

    NET --> PCAP
    PCAP --> FM
    FM --> FE
    FE --> XGB & IF
    XGB --> SHAP
    XGB & IF & SHAP --> RISK
    RISK --> PG
    RISK --> WS
    WS --> UI
    API <--> PG
    UI <--> API
```

---

## 🧠 Machine Learning & Threat Classification

SecureNet AI classifies network traffic across **15 granular categories**:

| ID | Class Label | Attack Family | Severity Score (0-100) |
|:---|:------------|:--------------|:-----------------------|
| 0 | `BENIGN` | Normal Traffic | 0 |
| 1 | `Bot` | Botnet Operations | 50 |
| 2 | `DDoS` | Distributed Denial of Service | 95 |
| 3 | `DoS GoldenEye` | Application-layer DoS | 85 |
| 4 | `DoS Hulk` | High-volume Web DoS | 85 |
| 5 | `FTP-Patator` | FTP Brute-force | 65 |
| 6 | `DoS slowloris` | Low-bandwidth HTTP DoS | 85 |
| 7 | `DoS Slowhttptest`| Slow HTTP Request Attack | 85 |
| 8 | `Heartbleed` | OpenSSL TLS Exploit | 100 |
| 9 | `Infiltration` | Internal Host Compromise | 95 |
| 10 | `PortScan` | Reconnaissance & Port Scanning | 55 |
| 11 | `SSH-Patator` | SSH Brute-force | 65 |
| 12 | `Web Attack - Brute Force` | Web Credential Guessing | 70 |
| 13 | `Web Attack - Sql Injection` | SQL Database Injection | 80 |
| 14 | `Web Attack - XSS` | Cross-Site Scripting | 70 |

---

## 📂 Project Structure

```
SecureNet-AI/
├── backend/                       # FastAPI Backend Core
│   ├── auth/                      # User authentication, JWT & Argon2
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── detection/                 # Detection storage & history routes
│   │   ├── models.py
│   │   └── routes.py
│   ├── realtime/                  # Live packet sniffer & flow engine
│   │   ├── detection_store.py
│   │   ├── feature_extractor.py
│   │   ├── flow_manager.py
│   │   ├── packet_capture.py
│   │   ├── realtime_detector.py
│   │   ├── realtime_router.py
│   │   └── ws_manager.py
│   ├── services/                  # ML pipeline wrapper service
│   │   └── ml_service.py
│   ├── config.py                  # API Configuration
│   ├── create_tables.py           # DB initialization & idempotent migrations
│   ├── db.py                      # SQLAlchemy session engine
│   └── main.py                    # Application entry point
│
├── frontend/                      # React (Vite) Cyber Command Dashboard
│   ├── src/
│   │   ├── api/                   # Axios client & API services
│   │   ├── components/            # UI Components (Sidebar, Charts, Modals)
│   │   ├── context/               # Auth & WebSocket contexts
│   │   ├── pages/                 # Dashboard, RealtimeMonitor, ThreatDetection, etc.
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── models/                        # Serialized ML & Anomaly Models
│   ├── xgboost_ids_model_v5.pkl   # Production Multi-Class XGBoost Model
│   ├── isolation_forest_model_v3.pkl # Production Anomaly Detector
│   └── label_encoder.pkl
│
├── src/                           # Machine Learning Source Pipeline
│   ├── predict.py                 # 🚀 Production Unified Prediction Pipeline
│   ├── training/                  # 🏋️ Training scripts for XGBoost & IF
│   ├── evaluation/                # 📊 Accuracy, Confusion Matrix, SHAP & Risk Scoring
│   └── data/                      # 🗃️ Preprocessing, Sampling, Splitting & ETL
│
├── reports/                       # Evaluation & Metric Output Reports
├── requirements.txt               # Python Dependencies
├── test_auth.py                   # Automated Auth & Prediction test suite
├── test_e2e.py                    # Full End-to-End System test suite
└── README.md
```

---

## ⚙️ Prerequisites

Before running the application, ensure you have:
- **Python 3.10+** (Python 3.11 / 3.12 / 3.13 supported)
- **Node.js 18+** & **npm**
- **PostgreSQL 14+**
- **Npcap** / **WinPcap** (on Windows) or **libpcap** (on Linux) if enabling live raw packet sniffing.

---

## 🛠️ Installation & Setup

### 1. Database Setup (PostgreSQL)

Ensure PostgreSQL is running locally and create the database:

```sql
CREATE DATABASE securenet_ai;
```

Configure your database connection parameters in `backend/db.py` or through environment variables:

```bash
# Example Database URL
DATABASE_URL=postgresql://postgres:password@localhost:5432/securenet_ai
```

Initialize the database schema:

```bash
python -m backend.create_tables
```

---

### 2. Backend Setup

1. **Create and activate a virtual environment:**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

---

### 3. Frontend Setup

1. **Navigate to the frontend directory:**

```bash
cd frontend
```

2. **Install Node dependencies:**

```bash
npm install
```

---

## 🚦 Running the Application

### 1. Start the Backend API & Sniffer Server

From the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- **API URL:** `http://127.0.0.1:8000`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **WebSocket Feed:** `ws://127.0.0.1:8000/ws/realtime`

---

### 2. Start the Frontend Dashboard

From the `frontend/` directory:

```bash
npm run dev
```
- **Dashboard UI:** `http://localhost:5173`

---

## 📚 API Documentation

Once the server is running, explore the interactive OpenAPI (Swagger) documentation at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Key Endpoints:

| Method | Endpoint | Description | Auth Required |
|:-------|:---------|:------------|:--------------|
| `POST` | `/auth/register` | Register a new security analyst account | No |
| `POST` | `/auth/login` | Authenticate and obtain JWT Bearer token | No |
| `GET` | `/auth/me` | Retrieve profile of authenticated user | Yes (JWT) |
| `POST` | `/predict` | Single network flow inference + SHAP explanation | Yes (JWT) |
| `GET` | `/detections/recent` | Fetch historical flagged detections | Yes (JWT) |
| `GET` | `/detections/stats` | Fetch aggregate threat distribution statistics | Yes (JWT) |
| `POST` | `/realtime/start` | Start live network packet sniffer | Yes (JWT) |
| `POST` | `/realtime/stop` | Stop live network packet sniffer | Yes (JWT) |
| `WS` | `/ws/realtime` | Real-time threat alert stream via WebSocket | Optional |

---

## 🧪 Testing

SecureNet AI includes automated unit, integration, and end-to-end test suites.

### Run All Real-Time & Store Unit Tests (52 tests):
```bash
pytest backend/realtime/ -v
```

### Run Authentication & API Pipeline Test:
```bash
python test_auth.py
```

### Run Full End-to-End System Test:
```bash
python test_e2e.py
```

---

## 🔒 Security & Privacy

- **No Raw Payload Retention:** Packet payloads are discarded immediately after 78-feature statistical extraction; only flow metadata and threat vectors are persisted.
- **Cryptographic Password Storage:** User credentials are encrypted using **Argon2** with strong memory/time cost parameters.
- **Secure Token Expiration:** JWT bearer tokens expire automatically to prevent session hijacking.
- **Defensive API Design:** Idempotent database schema migrations prevent data loss during continuous deployments.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
