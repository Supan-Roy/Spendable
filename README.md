# SPENDABLE 💡

> **"Know what you can safely spend."**

🏆 **Hackathon Track**: **Track 03: Customer Innovation & Financial Independence**  
🌐 **Live Deployment URL**: [https://spendable.supanroy.com/](https://spendable.supanroy.com/)

---

## 📌 Project Overview

### The Problem Addressed
Traditional banking applications, e-wallets, and personal finance tools present users with static account balances (e.g., *"Current Balance: ৳59,835"*). This creates a dangerous illusion of liquidity, leading users to overspend because it ignores upcoming bills, recurring subscriptions, rent, variable living expenses, and safety reserves. Users frequently experience end-of-month cash crunches, overdraft fees, and missed financial commitments.

### Proposed Solution & Purpose
**Spendable** solves this liquidity illusion by shifting the financial paradigm from *"What is my balance?"* to *"What can I safely spend today?"*. 

Spendable is an AI-powered personal financial runway and liquidity intelligence platform that calculates a real-time, non-double-counting **Spendable Capacity**:
$$\text{Spendable} = \max\left(0, \text{Current Balance} - \max(\text{Safety Reserve}, \text{Commitments})\right)$$

By combining point-in-time machine learning cash-flow forecasting, automated recurring commitment detection, What-If scenario simulation, and responsible Spendable AI guidance, Spendable empowers users to achieve true financial independence and confidence.

### Problem Validation (Macro Context)
Empirical data from the [World Bank Global Findex Database 2025](https://microdata.worldbank.org/catalog/7869/data-dictionary/F1?file_name=Findex_Microdata_2025_updateBangladesh) (Bangladesh Microdata 2024; variables `fin45`, `fin24a`, `fin24b`) highlights widespread financial-liquidity vulnerability:
- **62.7%**: State their greatest financial worry is having insufficient money for routine monthly expenses such as food, housing, or bills (`fin45`).
- **93.8%**: Report that raising emergency funds within 30 days would be very or somewhat difficult (`fin24a`).
- **60.4%**: Could cover essential living expenses for one month or less if their primary source of income disappeared (`fin24b`).

*These empirical indicators reflect baseline financial-liquidity vulnerability and cash-flow buffer constraints in the target demographic, demonstrating the systemic need for proactive liquidity visibility.*

---

## 🌐 Live Deployment URL

- **Live Application URL for Judges**: [https://spendable.supanroy.com/](https://spendable.supanroy.com/)
- **API Health Check Endpoint**: [https://spendable.supanroy.com/api/v1/health](https://spendable.supanroy.com/api/v1/health)

*(Note: The live deployment includes pre-configured demo personas (`acc_supan`, `acc_meraj`, `acc_sohana`, `acc_noman`, `acc_refat`) allowing judges to explore all features instantly without registration).*

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
- **AI Component Usage**: **Spendable AI** (Google Gemini 3.5 Flash Lite), a context-grounded conversational assistant that receives pre-computed financial facts to answer user queries with zero LLM arithmetic execution.

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
Spendable requires **zero manual registration** to evaluate. The app includes 5 pre-loaded canonical demo accounts:
- **`acc_supan` (Supan)**: Stable cash flow profile with regular monthly income and bill commitments (Current Balance: ৳321,000).
- **`acc_meraj` (Meraj)**: Tight liquidity persona with low-cash drawdown risk (Current Balance: ৳27,000).
- **`acc_sohana` (Sohana)**: Dynamic spending changes & variable category allocations (Current Balance: ৳308,000).
- **`acc_noman` (Noman)**: Variable income / freelance inflow persona (Current Balance: ৳321,000).
- **`acc_refat` (Refat)**: High recurring commitment burden persona (Current Balance: ৳192,000).

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

## 🧠 Machine Learning Methodology & Deep Evaluation (Phase 1 Judge Feedback Response)

To address Phase 1 judge evaluation feedback, this section details our target-generation pipeline, leakage-safe feature engineering, baseline performance comparisons across all horizons, high $R^2$ analysis, feature importances, and the exact mathematical derivation of the **Liquidity Pressure Classifier F1 = 86.75%**.

### 1. Target Generation Pipeline & Strict Point-in-Time Observability
- **Leakage-Safe Cutoff ($T$)**: Features are computed strictly using observable transaction records up to snapshot timestamp $T$ ($t \le T$). Ground-truth target metrics are calculated exclusively from forward window transactions $[T + 1, T + H]$ (for forecast horizons $H \in \{7, 14, 30\}$ days).
- **Target Definitions**:
  - `minimum_projected_balance` ($B_{\text{min}, H}$): $\min_{t \in [T+1, T+H]} \text{Balance}(t)$.
  - `expected_net_cash_flow` ($N_{H}$): $\sum_{t \in [T+1, T+H]} \text{Inflows}(t) - \sum_{t \in [T+1, T+H]} \text{Outflows}(t)$.
  - `liquidity_pressure_flag` ($P_{30\text{d}}$): Binary classification target $I(B_{\text{min}, 30\text{d}} < \text{Safety Threshold} \, [\text{৳15,000}])$.

### 2. Multi-Horizon Baseline Comparison (Held-Out Test Set: 1,649 Evaluation Snapshots)

| Horizon / Metric | Rolling Average Baseline | Recurring Commitment Baseline | HistGradientBoosting (Ours) | Performance Delta |
| :--- | :---: | :---: | :---: | :---: |
| **7-Day MAE (BDT)** | ৳16,972.14 | ৳16,842.70 | **৳13,982.08** | **+17.0% error reduction** |
| **7-Day $R^2$ Score** | 0.9923 | 0.9926 | **0.9946** | **+0.23% higher fit** |
| **14-Day MAE (BDT)** | ৳22,148.81 | ৳21,926.65 | **৳13,907.12** | **+36.6% error reduction** |
| **14-Day $R^2$ Score** | 0.9913 | 0.9919 | **0.9951** | **+0.32% higher fit** |
| **30-Day MAE (BDT)** | ৳28,418.56 | ৳27,750.43 | **৳14,682.01** | **+47.1% error reduction** |
| **30-Day RMSE (BDT)** | ৳41,137.53 | ৳38,998.73 | **৳23,903.56** | **+38.7% variance reduction** |
| **30-Day $R^2$ Score** | 0.9879 | 0.9891 | **0.9948** | **+0.57% higher fit** |

### 3. Analysis of $R^2 = 0.9948$ & Synthetic Data Characteristics
- **Mathematical Cause**: $R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}$. In our 500-persona benchmark dataset, initial user balances span a wide dynamic range (৳7,800 to ৳1,327,700), making total sum of squares ($\text{SS}_{\text{tot}}$) extremely large. Simultaneously, residual error ($\text{SS}_{\text{res}}$) remains bounded (MAE ৳14,682), producing high numerical $R^2 > 0.99$.
- **Synthetic Periodicity & Real-World Caveat**: Realistic synthetic generators model structured salary schedules and bill recurring intervals. While this validates algorithm capability on periodic data, real-world deployment will encounter unobserved cash activity and external bank accounts (acknowledged in our Limitations section).

### 4. Liquidity Pressure Classifier Evaluation ($F_1 = 86.75\%$)
- **Classification Objective**: Evaluates binary risk detection for predicting whether a user's minimum balance drops below the ৳15,000 safety threshold over the next 30 days.
- **Confusion Matrix & Metrics (1,649 Held-Out Test Snapshots)**:
  - True Positives (TP): 108 | False Positives (FP): 10 | False Negatives (FN): 23 | True Negatives (TN): 1,508
  - **Precision**: $\frac{108}{108 + 10} = 91.53\%$
  - **Recall**: $\frac{108}{108 + 23} = 82.44\%$
  - **F1-Score**: $2 \times \frac{0.9153 \times 0.8244}{0.9153 + 0.8244} = 86.75\%$
- **High-Vulnerability Persona Sub-Group**: On the `TIGHT_LIQUIDITY` persona sub-population (374 test snapshots), the model achieves **$F_1 = 95.45\%$** (MAE ৳3,149.90, RMSE ৳4,896.80), demonstrating high warning accuracy on financially vulnerable profiles.

### 5. Feature Importance Rankings (38-Feature Store)
1. `current_balance`: Baseline account liquid cash position.
2. `balance_min_30d`: Historical 30-day balance floor indicator.
3. `burn_rate_daily_30d`: Average daily cash expenditure velocity.
4. `recurring_outflow_30d`: Detected upcoming contractual bill commitments.
5. `net_cash_flow_30d`: Historical 30-day net cash flow trajectory.
6. `discretionary_outflow_ratio`: Ratio of non-essential spending vs total outflows.

---

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
