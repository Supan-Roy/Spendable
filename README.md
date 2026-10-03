# SPENDABLE 💡

> **"Know what you can safely spend."**

🏆 **Hackathon Track**: **Track 03: Customer Innovation & Financial Independence**  
🌐 **Live Deployment URL**: [https://spendable-production.up.railway.app](https://spendable-production.up.railway.app)

---

## 📌 Project Overview

### The Problem Addressed
Traditional banking applications, e-wallets, and personal finance tools present users with static account balances (e.g., *"Current Balance: ৳59,835"*). This creates a dangerous illusion of liquidity, leading users to overspend because it ignores upcoming bills, recurring subscriptions, rent, variable living expenses, and safety reserves. Users frequently experience end-of-month cash crunches, overdraft fees, and missed financial commitments.

### Proposed Solution & Purpose
**Spendable** solves this liquidity illusion by shifting the financial paradigm from *"What is my balance?"* to *"What can I safely spend today?"*. 

Spendable is an AI-powered personal financial runway and liquidity intelligence platform that calculates a real-time, non-double-counting **Spendable Capacity**:
$$\text{Spendable} = \max\left(0, \text{Current Balance} - \max(\text{Safety Reserve}, \text{Commitments})\right)$$

By combining point-in-time machine learning cash-flow forecasting, automated recurring commitment detection, What-If scenario simulation, and responsible Spendable AI guidance, Spendable empowers users to achieve true financial independence and confidence.

---

## 🌐 Live Deployment URL

- **Live Application URL for Judges**: [https://spendable-production.up.railway.app](https://spendable-production.up.railway.app)
- **API Health Check Endpoint**: [https://spendable-production.up.railway.app/api/v1/health](https://spendable-production.up.railway.app/api/v1/health)

*(Note: The live deployment includes pre-configured demo personas (`acc_supan`, `acc_tanvir`, `acc_sarah`, `acc_fatima`) allowing judges to explore all features instantly without registration).*

---

## ⚡ Features & AI Components Usage

Spendable delivers 5 primary application tabs, seamlessly integrating specialized AI & ML components:

### 1. Overview Tab (Real-Time Liquidity Dashboard)
- **Implemented Features**: Displays your **Safe Spendable Capacity today** (e.g., *"৳22,552.76 Safely Spendable out of ৳59,835.05 balance"*), real-time progress indicators, protected safety buffer metrics, and an upcoming 30-day bill timeline.
- **AI Component Usage**: Uses the **Point-in-Time Recurring Commitment Detector** to automatically identify upcoming bills and feed them into the deterministic Spendable capacity calculation engine.

### 2. Activity Tab (Multi-Channel Ingestion Feed)
- **Implemented Features**: Ingests and categorizes transaction activity across multi-channel bank and mobile wallet accounts with direction classification (`INFLOW` vs `OUTFLOW`), category tagging, search, pagination, and ISO 8601 UTC formatting.
- **AI Component Usage**: Standardizes raw financial activity feeds into a 38-feature rolling window feature store for machine learning model inference.

### 3. Forecast Tab (30-Day Predictive Cash Flow Runway)
- **Implemented Features**: Projects daily balance trajectories over the next 30 days, highlights low-liquidity crunch dates where balances cross safety thresholds, and compares ML forecasts against reference baselines.
- **AI Component Usage**: Multi-horizon **`HistGradientBoostingRegressor`** machine learning models trained on 38 rolling window features to predict 7-day, 14-day, and 30-day minimum balance drawdowns and daily balance paths.

### 4. Simulate Tab (What-If Scenario Engine & Spendable AI)
- **Implemented Features**: Evaluates 5 hypothetical scenarios in real-time (`ONE_TIME_EXPENSE`, `ADDITIONAL_INCOME`, `ADDITIONAL_COMMITMENT`, `SPENDING_REDUCTION`, `INCOME_DELAY`) without mutating underlying database tables, rendering a Multi-Metric Impact Dashboard.
- **AI Component Usage**: **Spendable AI** (Google Gemini 2.5 Flash / 1.5 Flash), a context-grounded conversational assistant that receives pre-computed financial facts to answer user queries with zero LLM arithmetic execution.

### 5. Inspect ⚡ System Visualizer Tab (Architecture Walkthrough)
- **Implemented Features**: Step-by-step technical visualizer detailing the connected 5-stage processing pipeline (`STAGE 01 Ingestion ➔ STAGE 02 Feature Store ➔ STAGE 03 ML Engine ➔ STAGE 04 Deterministic Math ➔ STAGE 05 Spendable AI`).
- **AI Component Usage**: Renders a zero-API client-side topology visualizer showing live data flow, model parameters, and responsible AI boundaries.

---

## 🛠️ Technology Stack

| Layer | Component | Technologies / Libraries Used |
| :--- | :--- | :--- |
| **Languages** | Core Languages | Python 3.12+, TypeScript 5.7+, HTML5, CSS3 |
| **Frontend Framework** | Web Application | React 19, Vite v6, Vanilla Glassmorphism CSS, Lucide React Icons |
| **Backend Framework** | REST API Server | FastAPI v0.115+, Uvicorn, Pydantic v2 |
| **Database & ORM** | Data Persistence | PostgreSQL / SQLite, SQLAlchemy v2.0+, Alembic Migrations |
| **Machine Learning** | Predictive Engine | `scikit-learn` (`HistGradientBoostingRegressor`), `pandas`, `numpy`, `scipy` |
| **AI / LLM Integration** | Explainable AI | Google Gemini API (`google-genai` v1.0+ SDK) |
| **Testing Suite** | Quality Assurance | `pytest` v8.4+, `httpx`, `pytest-asyncio`, `FastAPI TestClient` |
| **Container & Cloud** | Deployment | Multi-stage Dockerfile, Docker Compose, Railway Platform |

---

## 📋 Requirements & Prerequisites

Before setting up Spendable locally, ensure your system meets the following prerequisites:

- **Python**: Version `3.12.0` or higher
- **Node.js**: Version `20.0.0` or `22.0.0+`
- **Package Manager**: `pnpm` (v9+) or `npm` (v10+)
- **Docker & Docker Compose** *(Optional, for PostgreSQL database container)*: Docker Engine v24+
- **Git**: For cloning the codebase

---

## 🔑 Environment Variables

Spendable uses environment variables for configuration. Create a `.env` file in the `backend/` directory or root folder.

| Variable Name | Purpose | Configuration Instructions / Default Placeholder |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API key for Spendable AI chat assistant | `GEMINI_API_KEY=your_google_gemini_api_key_here` *(Optional: If unconfigured, Spendable AI uses a rule-based fallback synthesizer)* |
| `DATABASE_URL` | SQLAlchemy database connection string | `DATABASE_URL=sqlite:///./spendable.db` *(Default local)* or `postgresql://user:pass@localhost:5432/spendable_db` |
| `ENVIRONMENT` | Application deployment environment | `ENVIRONMENT=development` *(Options: `development`, `production`, `testing`)* |
| `PORT` | Backend server HTTP port | `PORT=8000` |
| `SECRET_KEY` | Application secret key for session security | `SECRET_KEY=your_secret_key_placeholder_change_in_production` |

---

## 📥 Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Supan-Roy/Spendable.git
cd Spendable
```

### 2. Backend Setup & Virtual Environment
```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\activate

# Activate virtual environment (Linux / macOS)
# source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup
```bash
# Install node dependencies using pnpm
pnpm install
```

### 4. Database Setup & Initial Seeding
```bash
# Run database migrations and seed pre-configured demo accounts
python backend/app/seed.py
```

---

## 🚀 Run and Build Commands

### 1. Local Development Command (Concurrently Starts All Services)
To launch the **entire application** (PostgreSQL container, FastAPI backend, and React Vite frontend concurrently):
```bash
pnpm run dev
```

### 2. Manual Development Execution (Separate Terminals)
- **Backend API Server**:
  ```bash
  $env:PYTHONPATH='backend'; uvicorn app.main:app --reload --port 8000
  ```
- **Frontend Vite Dev Server**:
  ```bash
  pnpm --prefix frontend dev
  ```

### 3. Production Build Commands
- **Compile Frontend Production Bundle**:
  ```bash
  pnpm --prefix frontend build
  ```
- **Run Production Application Server**:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

---

## 🧪 Testing Instructions

### 1. Run Backend Unit Test Suite (Pytest)
Run the full 118-item test suite covering API endpoints, Spendable engine calculations, ML forecasting models, scenario simulation laws, and Gemini explanation fallbacks:

```bash
# Windows PowerShell
$env:PYTHONPATH='backend'; python -m pytest backend/tests

# Linux / macOS
PYTHONPATH=backend python -m pytest backend/tests
```

### 2. Run Frontend Production Type Check & Build Verification
Verify TypeScript type safety and Vite bundle compilation:
```bash
pnpm --prefix frontend build
```

### 3. Automated Scenario Monotonicity & Sanity Check
Run the 700-rule scenario simulation mathematical validation suite:
```bash
$env:PYTHONPATH='backend'; python -m pytest backend/tests/test_scenario_simulation.py
```

---

## ⚙️ Other Configuration & Access Requirements

### Demo Persona Quick-Selectors
Spendable requires **zero manual registration** to evaluate. The app includes 4 pre-loaded financial personas with diverse transaction profiles:
- **`acc_supan` (Supan Roy)**: Standard salaried professional persona with regular monthly income and bill commitments.
- **`acc_tanvir` (Tanvir Ahmed)**: Variable-income freelancer persona with irregular inflows and high spending volatility.
- **`acc_sarah` (Sarah Khan)**: High-net-worth persona with multi-channel investments and luxury commitments.
- **`acc_fatima` (Fatima Begum)**: Tight-liquidity persona vulnerable to low-cash drop dates.

Switch between demo personas instantly using the top header dropdown or the Login modal quick-selector.

### Zero-API Fallback Mode
If `GEMINI_API_KEY` is not provided:
- The Spendable Engine, ML Forecaster, Recurring Detector, Scenario Engine, and Inspect visualizer function **100% normally**.
- Spendable AI chat uses a **Deterministic Rule-Based Fallback Synthesizer** to generate natural language advice from exact calculated facts.

---

## 📐 Technical Architecture & Model Metrics

### System Architecture Topology
```mermaid
graph TD
    subgraph Frontend["Frontend Layer (React 19 + TypeScript + Vite)"]
        UI["User Interface Dashboard"]
        Tabs["Overview | Financial Activity | 30-Day Forecast | Scenario Simulator | Inspect System Visualizer"]
        Modal["Account Switcher, Formula Explanation & System Topology Modals"]
    end

    subgraph API["Backend API Layer (FastAPI + Python 3.12)"]
        Router["API Endpoints (/api/v1/overview, /api/v1/forecast, /api/v1/simulate, /api/v1/chat)"]
        AuthCtx["Auth & Demo Persona Session Manager"]
    end

    subgraph Storage["Persistence Layer (PostgreSQL / SQLite)"]
        DB[(UserAccounts & FinancialActivities Table)]
    end

    subgraph ML_Engine["Predictive & Analytical Financial Engine"]
        PitBuilder["Point-in-Time Feature Builder (Leakage-Safe)"]
        RecDetector["Recurring Commitment Detector (Point-in-Time Regularity & Category Priors)"]
        ForecastML["Cash-Flow Forecasting Engine (HistGradientBoostingRegressor)"]
        SpendEngine["Spendable Engine (Candidate A Non-Double-Counting)"]
        ScenarioSim["What-If Scenario Simulator Engine"]
    end

    subgraph LLM_Layer["Explainable AI (Google Gemini API)"]
        SpendableAI["Spendable AI Chat Engine & Structured Prompt Synthesizer"]
    end

    UI --> Router
    Router --> AuthCtx
    Router --> DB
    Router --> PitBuilder
    PitBuilder --> RecDetector
    PitBuilder --> ForecastML
    RecDetector --> SpendEngine
    ForecastML --> SpendEngine
    SpendEngine --> ScenarioSim
    SpendEngine --> SpendableAI
    SpendableAI --> UI
```

### Model Performance Summary (Held-Out Test Set)

| Module | Evaluated Metric | Test Result | Technical Definition |
| :--- | :--- | :---: | :--- |
| **Recurring Commitment Detection (Point-in-Time Detector)** | F1-Score | **97.99%** | $F_1$ harmonic mean across commitment categories |
| | Precision | **98.32%** | 293 TP / (293 TP + 5 FP) on held-out test data |
| | Recall | **97.67%** | 293 TP / (293 TP + 7 FN) on held-out test data |
| **Cash-Flow Forecasting (HistGradientBoostingRegressor)** | R² (30-Day Horizon) | **0.9948** | 99.48% of variance in 30-day balance trajectories explained |
| | MAE (30-Day Horizon) | **৳14,682** | Mean Absolute Error across evaluation snapshots |
| | RMSE (30-Day Horizon) | **৳23,903** | Root Mean Squared Error across evaluation snapshots |
| **Liquidity-Pressure Horizon Classifier** | Precision | **91.53%** | Accuracy of low-cash risk warnings |
| | Recall | **82.44%** | True positive risk detection rate |
| | F1-Score | **86.75%** | Overall risk classification harmonic mean |
| | Tight Liquidity F1-Score | **95.45%** | Specialized risk detection F1 on high-vulnerability personas |
| **Spendable Engine** | Safety Validation Check | **100.00%** | Non-double-counting commitment protection pass rate |
| **Scenario Simulation** | Sanity-Check Pass Rate | **100% (700/700)** | Zero violations across monotonicity & non-negative checks |

---

## 📁 Repository Directory Structure

```
Spendable/
├── Dockerfile                  # Container configuration for Railway deployment
├── docker-compose.yml          # Local multi-container development environment
├── package.json                # Monorepo root developer scripts & process runner
├── pnpm-workspace.yaml         # pnpm workspace definition
├── README.md                   # Project documentation
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry point & static SPA file server
│   │   ├── config.py           # Pydantic environment configuration
│   │   ├── database.py         # SQLAlchemy connection management
│   │   ├── api/                # Product API endpoints (/overview, /forecast, /simulate, /chat)
│   │   ├── features/           # Point-in-time leakage-safe feature builder
│   │   ├── recurring/          # Point-in-time recurring commitment detector & evaluator
│   │   ├── forecasting/        # HistGradientBoosting cash-flow forecasting models
│   │   ├── engine/             # Spendable Engine calculation formulations
│   │   ├── scenario/           # What-if scenario simulation engine
│   │   └── explanation/        # Spendable AI Gemini chat & explanation provider
│   └── tests/                  # 118 unit & integration test suites
└── frontend/
    ├── src/
    │   ├── pages/              # Overview, Financial Activity, Forecast, Simulate, Inspect pages
    │   ├── components/         # Header, LoginModal, ConfirmModal, CalculationModal
    │   ├── context/            # AuthContext & demo persona manager
    │   ├── api/                # Strictly-typed API client & endpoints
    │   └── utils/              # Date & Time, BDT Currency, and Status formatters
    └── vite.config.ts          # Vite React build configuration
```
