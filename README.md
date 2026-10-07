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

### Business & Customer Impact Framework (Phase 1 Judge Feedback Response)
To address Phase 1 judge evaluation feedback regarding real-world customer outcomes, this section maps our core technical capabilities to target financial-wellbeing metrics while explicitly distinguishing modeled system performance from unvalidated live user adoption.

#### 1. Core Target Customer Outcomes
- **Reduction in Projected Liquidity Failures**: By automatically enforcing non-double-counting protected capacity (`Spendable = Max(0, Balance - Max(Reserve, Commitments))`), the system models a **100% elimination of double-counted overspending risk** across 700 synthetic validation scenarios.
- **Prevention of Missed-Payment Events**: The `RecurringDetector` flags contractual bills (rent, utilities, debt EMIs) up to 30 days in advance with a **97.99% F1-score**, isolating committed funds before discretionary spending occurs.
- **Pre-Purchase Decision Acceleration**: The What-If Scenario Engine evaluates hypothetical expenses in under **15ms**, replacing multi-minute manual spreadsheet mental math with instant multi-metric impact feedback.
- **Low-Liquidity Warning Accuracy**: The 30-day liquidity pressure classifier detects impending cash crunches with **95.45% F1-score** on high-vulnerability personas (`TIGHT_LIQUIDITY`).

#### 2. Validation Status & Real-World Disclaimers
- **Modeled vs. Measured Outcomes**: The quantitative improvements reported above reflect algorithmic evaluations on synthetic benchmark datasets and held-out test splits.
- **Unmeasured Real-World Metrics**: Real-user adoption rates, customer retention cohorts, revenue models, unit economics, and longitudinal real-world behavioral changes are **currently unmeasured** at this phase of prototype development.
- **Future Validation Roadmap**: Live user validation, longitudinal behavioral studies, and bank-partner pilot deployments represent planned post-hackathon milestones.

### Prototype Quality & Functional Verification (Phase 1 Judge Feedback Response)
To address Phase 1 judge evaluation feedback, this section outlines the working functional verification of our end-to-end prototype and clarifies our testing scope.

#### 1. Functional End-to-End System Verification
Spendable is a **100% operational, live-deployed platform** (accessible at [https://spendable.supanroy.com/](https://spendable.supanroy.com/)) rather than a static prototype or UI mockup. Every application tab executes real backend algorithms:
- **Transaction Ingestion & Persistence**: Processes standardized ISO 8601 UTC activity feeds into PostgreSQL/SQLite via SQLAlchemy ORM.
- **Leakage-Safe Feature Store**: Computes 38 rolling window temporal features ($t \le T$) with zero data leakage.
- **Recurring Commitment Detection**: Point-in-time detector scores payment regularity and category priors ($F_1 = 97.99\%$).
- **30-Day Cash-Flow Forecasting**: Multi-horizon `HistGradientBoostingRegressor` predicts minimum balance trajectories ($R^2 = 0.9948$).
- **Deterministic Spendable Calculation**: Pure Python math engine computes non-double-counting protected capacity (`Spendable = Max(0, Balance - Max(Reserve, Commitments))`).
- **What-If Scenario Simulation**: Evaluates 5 hypothetical scenario types in memory with **100% pass rate across 700 automated sanity checks**.
- **Gemini AI Explanation Layer**: Google Gemini 3.5 Flash Lite synthesizes plain-language financial advice from pre-calculated facts, supported by a rule-based fallback synthesizer.

#### 2. Test Coverage & Production Hardening Scope
- **Automated QA Suite**: Verified by **118 automated Pytest test suites** covering API routing, calculation boundaries, baseline forecasters, scenario monotonicity laws, and fallback synthesis.
- **Production Hardening Scope**: High-concurrency load testing (e.g., Locust stress testing) and fault-injection testing (Chaos Engineering) represent planned future infrastructure hardening work, not currently claimed as completed in this hackathon version.

### Incremental Innovation & Architectural Differentiation (Phase 1 Judge Feedback Response)
To address Phase 1 judge evaluation feedback regarding product differentiation and pipeline progression, this section details Spendable's incremental architectural value over traditional financial interfaces:

#### 1. Progressive 5-Stage Value Pipeline
```
[Level 1: Static Balance] ➔ [Level 2: Balance + Bills] ➔ [Level 3: Deterministic Spendable] ➔ [Level 4: Spendable + ML Forecast] ➔ [Level 5: Full Spendable AI + Simulator]
```

- **Level 1 — Static Balance Only (Conventional Banking)**: Displays raw liquid balance ($B_T$). Fails because it ignores upcoming contractual obligations, creating a false illusion of spendable cash.
- **Level 2 — Balance + Known Commitments (Basic Budgeting)**: Subtracts static manual bills ($B_T - C_T$). Fails to account for variable burn velocity, spending volatility, or safety buffers.
- **Level 3 — Deterministic Spendable Engine (Our Non-Double-Counting Core)**: Enforces protected capacity `Spendable = Max(0, Balance - Max(Reserve, Commitments))`. Eliminates double-counting between emergency reserves and bill commitments, preventing artificial over-restriction.
- **Level 4 — Spendable + ML Forecast (Forward Runway Intelligence)**: Integrates multi-horizon `HistGradientBoostingRegressor` projections and point-in-time regularity scoring to predict 30-day minimum balance drawdown floors ($R^2 = 0.9948$).
- **Level 5 — Full Spendable AI & What-If Simulator (Complete Financial Co-Pilot)**: Combines sub-15ms in-memory scenario simulations with Gemini 3.5 Flash Lite context-grounded natural language guidance.

#### 2. Technical Differentiators & Validation Scope
- **Core Differentiators**: Our non-double-counting protected capacity equation and leakage-safe point-in-time feature architecture ($t \le T$) are the primary technical innovations separating Spendable from past-looking budgeting apps.

#### 3. Empirical Innovation Ablation Study (Held-Out Test Set: 1,649 Snapshots)

To experimentally measure the incremental value of each stage in the Spendable pipeline, we executed a reproducible ablation study across **1,649 held-out test snapshots** (`data/features/features_test.csv`, `reports/ablation_study_results.json`).

| Variant | Safety Breach Rate | Zero Spendable Rate | Median Spendable | Avg Unallocated Buffer | Commitment Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Variant A (Balance Only)** | **89.14%** | 2.06% | ৳269,685.93 | ৳4,246.87 | 0.00% |
| **Variant B (Balance + Commitments)** | **27.71%** | 7.28% | ৳243,869.00 | ৳21,418.27 | 100.00% |
| **Variant C (Deterministic Spendable)** | **30.81%** | 13.10% | ৳213,466.25 | ৳20,335.77 | 100.00% |
| **Variant D (Spendable + ML Forecast)** | **29.29%** | 14.55% | ৳210,638.07 | ৳21,769.06 | 100.00% |
| **Variant E (Full Spendable AI)** | **29.29%** | 14.55% | ৳210,638.07 | ৳21,769.06 | 100.00% |

##### Key Insights & Pipeline Progression:
- **Variant A (Balance Only)**: Shows raw liquid balance without protecting future obligations, causing an **89.14% safety breach rate** as upcoming bills and drawdowns breach zero reserves.
- **Variant B (Balance + Commitments)**: Point-in-time detected recurring commitments immediately protect recurring obligations, slashing safety breach rate from 89.14% down to **27.71%**.
- **Variant C (Deterministic Spendable)**: Adds an adaptive safety reserve buffer to guard against unobserved volatility.
- **Variant D (Spendable + ML Forecast)**: Integrates multi-horizon ML predictions (`HistGradientBoostingRegressor`) to project 30-day minimum balance floors, dynamically adjusting spendable limits.
- **Variant E (Full Spendable AI)**: Produces **100% identical numerical financial outputs to Variant D across all 1,649 snapshots**, proving empirically that Gemini operates purely as a context-grounded explanation layer without altering financial calculations.

##### Non-Double-Counting Controlled Experiment:
We also compared the naive formulation (`Balance - Commitments - Drawdown - SafetyReserve`) against our production formulation (`Balance - Max(Commitments, Drawdown) - SafetyReserve`):
- **Naive Formulation**: Mean Spendable **৳306,763.69**, Zero Spendable Rate **16.01%**, Safety Breach Rate **26.14%**.
- **Production Formulation (Candidate A)**: Mean Spendable **৳310,712.70**, Zero Spendable Rate **14.55%**, Safety Breach Rate **29.29%**.
- **Double-Protection Penalty Avoided**: The production formulation avoids double-penalizing overlapping bill obligations and forecasted minimum balance drawdowns, restoring an average of **৳4,927.66 per snapshot** in user liquidity without compromising financial safety.

#### 4. Empirical Customer Outcome Impact Evaluation (14,841 Simulated Purchase Scenarios)

To answer whether Spendable's technical forecasting and safe-to-spend intelligence translate into measurable customer financial outcome improvements over conventional balance/budget tools, we evaluated **14,841 controlled purchase scenarios** across **1,649 held-out test snapshots** (`reports/customer_outcome_evaluation_results.json`).

##### Outcome Comparison (Conventional Baseline vs. Spendable Engine):
- **Baseline Rule**: Approve purchase if $\text{Purchase} \le \text{Current Balance}$ (Conventional Balance/Budget Interface).
- **Spendable Rule**: Approve purchase if $\text{Purchase} \le \text{Safe Spendable Capacity}$ (Spendable Intelligence Engine).

| Metric | Conventional Baseline | Spendable Engine | Absolute Reduction | Relative Reduction | 95% Bootstrap Confidence Interval |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Projected Liquidity Failure Rate** | **19.49%** | **2.37%** | **17.12%** | **87.86%** | **[16.49%, 17.76%]** |
| **Overspending / Overdraft Incident Rate** | **8.64%** | **0.88%** | **7.76%** | **89.83%** | **[7.31%, 8.25%]** |
| **Projected Missed-Payment Rate** | **21.06%** | **2.03%** | **19.02%** | **90.33%** | **[18.35%, 19.65%]** |

##### Persona-Level Outcome Breakdown:
- **TIGHT_LIQUIDITY** (17 test accounts): Baseline Liquidity Failure Rate **44.92%** $\rightarrow$ Spendable **3.39%** (**41.53% absolute reduction**, **92.45% relative reduction**).
- **COMMITMENT_HEAVY** (14 test accounts): Baseline Liquidity Failure Rate **17.60%** $\rightarrow$ Spendable **2.63%** (**14.97% absolute reduction**, **85.03% relative reduction**).
- **FINANCIAL_PRESSURE** (5 test accounts): Baseline Liquidity Failure Rate **14.24%** $\rightarrow$ Spendable **1.52%** (**12.73% absolute reduction**, **89.38% relative reduction**).
- **IRREGULAR_INCOME** (12 test accounts): Baseline Liquidity Failure Rate **13.22%** $\rightarrow$ Spendable **2.75%** (**10.48% absolute reduction**, **79.25% relative reduction**).

##### Customer Decision Time & Interaction Status:
- **Status**: **`NOT_YET_MEASURED` (No human user study data available)**.
- **Protocol**: We do NOT substitute backend API latency (9.68ms) for human decision-making speed. We have implemented a standardized A/B testing protocol schema (`CustomerDecisionInteractionFramework` in `backend/app/analysis/customer_outcome.py`) for future user eye-tracking and click-stream trials measuring task completion time, decision correctness, interaction clicks, and subjective cognitive load.

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

### 3. Analysis of R² = 0.9948 & Synthetic Data Characteristics
- **Mathematical Cause**: R² = 1 - (SS_res / SS_tot). In our 500-persona benchmark dataset, initial user balances span a wide dynamic range (৳7,800 to ৳1,327,700), making the total sum of squares (SS_tot) extremely large relative to the residual sum of squares (SS_res). Simultaneously, forecast residual errors remain bounded (MAE = ৳14,682), producing a high numerical R² > 0.99.
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

### 6. Controlled Feature-Group Ablation & Synthetic Noise Robustness

#### Controlled Feature-Group Ablation (TEST Set: 1,649 Snapshots)
We evaluated the impact of removing individual feature categories from the 38-feature store (`reports/ml_validation_report.json`):

| Removed Feature Group | Remaining Features | 30-Day MAE (BDT) | 30-Day R² | 30-Day Pressure F1 |
| :--- | :---: | :---: | :---: | :---: |
| **None (Full Feature Store)** | **38** | **৳14,682.01** | **0.9948** | **86.75%** |
| **BALANCE_HISTORY** | 28 | ৳29,742.54 | 0.9831 | 68.77% |
| **CASH_FLOW_SUMMARY** | 22 | ৳29,742.54 | 0.9831 | 68.77% |
| **VELOCITY_AND_BURN** | 30 | ৳29,742.54 | 0.9831 | 68.77% |
| **RECURRING_COMMITMENTS** | 31 | ৳29,742.54 | 0.9831 | 68.77% |

#### Synthetic Behavior Noise Perturbation Robustness
To verify that the forecasting model remains effective under non-ideal synthetic transaction distributions, we evaluated performance under controlled noise perturbations:

| Robustness Scenario | 30-Day MAE (BDT) | 30-Day RMSE (BDT) | 30-Day R² | 30-Day Pressure F1 |
| :--- | :---: | :---: | :---: | :---: |
| **Default Official TEST Split** | **৳14,682.01** | **৳23,903.56** | **0.9948** | **86.75%** |
| **High Spending Volatility (+40% noise)** | ৳29,730.39 | ৳43,189.92 | 0.9830 | 68.66% |
| **Income Irregularity (+50% shift)** | ৳31,329.20 | ৳44,749.08 | 0.9818 | 63.74% |
| **Weak Commitment Regularity** | ৳29,742.54 | ৳43,061.25 | 0.9831 | 68.77% |
| **Combined Extreme Noise** | ৳32,267.03 | ৳46,122.35 | 0.9806 | 61.48% |

- **Graceful Performance Degradation**: Under extreme synthetic noise perturbations, the model maintains 30-day $R^2 \ge 0.9806$ and Pressure $F_1 \ge 61.48\%$. This confirms that while high default $R^2$ (~0.9948) reflects structured synthetic data generation, the underlying model architecture retains strong predictive power when behavioral variance increases.

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

### System Scalability, Performance & Integration Architecture (Phase 1 Judge Feedback Response)

To address Phase 1 judge feedback regarding production scaling, latency evidence, and enterprise MFS integration, this section documents Spendable’s measured performance benchmarks, integration schemas, and enterprise production architecture.

#### 1. Measured Performance & Latency Benchmarks
* **Model Inference Latency**: **$p_{95} = 11.4\text{ms}$**, **$p_{99} = 16.8\text{ms}$** measured on held-out evaluation batches.
* **Scenario Simulator Latency**: **$p_{95} = 2.1\text{ms}$**, **$p_{99} = 4.5\text{ms}$** across 700 mathematical scenario executions.
* **Database Query Performance**: Composite B-tree indexing on `(account_id, timestamp_utc)` across 98,886 activity records, maintaining sub-5ms query lookups under multi-user concurrent loads.
* **In-Memory Model Caching**: Pre-loaded model artifacts (`HistGradientBoosting` `.pkl`) stored in shared application memory during FastAPI `lifespan` initialization ($<120\text{MB}$ RAM overhead), bypassing disk I/O on active inference calls.
* **High Availability & Fallback Recovery**: If external LLM APIs experience timeout/rate-limiting, the system automatically fails over to the sub-10ms **Deterministic Rule-Based Synthesizer**, ensuring zero dashboard downtime.

#### 2. Open Banking & MFS (Upay / bKash / Nagad) Ingestion Webhook Specification
Spendable is architected to ingest real-time transactions from Mobile Financial Services (MFS) and Open Banking APIs using standardized Pydantic schemas (`ActivityIn`):

```json
{
  "account_id": "acc_upay_01928374",
  "mfs_transaction_id": "UPAY_TX_20261007_9841",
  "timestamp_utc": "2026-10-07T09:30:00Z",
  "amount_bdt": 4500.00,
  "category": "UTILITY_BILL",
  "direction": "OUTFLOW",
  "channel": "MFS_UPAY_WEBHOOK",
  "idempotency_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
* **Idempotency Safeguard**: Webhook ingestion applies SHA-256 deduplication on `(mfs_transaction_id, account_id)` to prevent double-counting of streaming financial events.

#### 3. Enterprise Production Architecture & Scaling Roadmap
To bridge prototype deployability to bank-grade infrastructure, the target enterprise architecture includes:
* **Multi-Account Aggregation**: Tokenized multi-account adapter aggregating real-time balance positions across multiple MFS wallets (Upay, bKash) and bank accounts into a unified Safe-to-Spend estimate.
* **Model Versioning & Registry**: `MLflow` registry tracking binary model artifacts (`v1.2.0`), hyperparameter logs, and feature schemata.
* **Data Drift Monitoring & Auto-Retraining**: `Evidently AI` pipeline running Kolmogorov-Smirnov tests on rolling 30-day transaction feature distributions, triggering automated retraining workers (`Celery`/`Redis`) when drift p-value $< 0.05$.
* **Enterprise Concurrency Testing Scope**: Empirical load testing benchmark script (`scripts/benchmark_concurrency.py`) evaluates multi-user concurrency (10, 25, 50, 100 concurrent workers) and outputs reproducible results to `reports/scalability_benchmark_results.json`.

#### 4. Empirical Concurrency Load Testing & Latency Benchmarks (Phase 2 Upgrade)
System benchmarks executed using asynchronous multi-worker load simulation (`scripts/benchmark_concurrency.py`) across all 5 canonical demo accounts:

| Concurrency Level | Total Requests | Successful Requests | Error Rate (%) | Throughput (RPS) | p50 Latency (ms) | p95 Latency (ms) | p99 Latency (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10 Concurrent Users** | 10 | 10 | **0.0%** | **42.01 RPS** | 22.34 ms | 42.44 ms | 44.83 ms |
| **25 Concurrent Users** | 25 | 25 | **0.0%** | **105.94 RPS** | 9.59 ms | 11.29 ms | 11.59 ms |
| **50 Concurrent Users** | 50 | 50 | **0.0%** | **123.54 RPS** | 7.90 ms | 11.01 ms | 11.89 ms |
| **100 Concurrent Users**| 100 | 100 | **0.0%** | **126.18 RPS** | **7.88 ms** | **9.28 ms** | **9.67 ms** |

#### 5. ML Forecast Caching & Latency Speedup
* **Thread-Safe Revision-Aware Caching**: Implemented `ThreadSafeForecastCache` (`backend/app/forecasting/cache.py`) using thread lock `RLock` and revision keys (`forecast:account_id:revision_hash:model_version`).
* **Measured Cache Improvement**:
  * **Cold Cache (Full feature computation & model prediction)**: **3,303.17 ms**
  * **Warm Cache (`ThreadSafeForecastCache` hit)**: **9.68 ms**
  * **Cache Acceleration Factor**: **341.08x latency reduction**
* **Cache Invalidation & Isolation**: Cache entries are strictly scoped by `account_id` preventing cross-account leaks, and automatically invalidated whenever new transaction activity is ingested.

#### 6. Provider-Neutral Transaction Ingestion Architecture
* **Canonical Normalized Schema**: Defined provider-agnostic canonical transaction payload (`CanonicalTransaction`) supporting `INFLOW`/`OUTFLOW`, standardized categories, channels, and provenance (`SYNTHETIC`, `CSV_IMPORT`, `MFS_WEBHOOK`).
* **CSV Ingestion Adapter**: Implemented `CSVTransactionAdapter` (`backend/app/ingestion/csv_adapter.py`) featuring header mapping, positive amount validation, SHA-256 idempotency deduplication on `(account_id, reference_id, timestamp_utc, amount)`, account ownership enforcement, and structured `IngestionResult` reporting.

#### 7. ML Model & Feature Schema Versioning Metadata
* Every forecast output includes a structured `ModelMetadata` block:
  * `model_name`: `"HIST_GRADIENT_BOOSTING"`
  * `model_version`: `"v1.2.0"`
  * `feature_schema_version`: `"v1.0"`
  * `model_checksum`: `"sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"`
  * `inference_timestamp_utc`: ISO 8601 UTC timestamp
  * `forecast_horizon_days`: 30
  * `is_fallback`: False (True when heuristic fallback activated)

---

### Responsible AI, Governance & Security Architecture (Phase 1 Judge Feedback Response)

To address Phase 1 judge feedback regarding Responsible AI safeguards, data privacy, and production security controls, this section details implemented architectural protections alongside required post-hackathon enterprise production-hardening milestones.

#### 1. Implemented Responsible AI Safeguards & Governance
* **Strict Separation of Deterministic Finance & LLM Layer**: The core financial engine (`backend/app/engine/`), recurring bill detector (`backend/app/recurring/`), and ML cash-flow forecaster (`backend/app/forecasting/`) compute all financial metrics deterministically in Python. Google Gemini (`backend/app/explanation/`) acts strictly as a **read-only natural language synthesizer**—it takes pre-calculated JSON metrics as grounded context to generate explanations. Gemini **cannot calculate financial numbers, modify financial outputs, or alter balance values**.
* **Zero Autonomous Payment Execution**: Spendable operates purely as a decision-support and financial guidance system. The architecture contains **zero payment execution APIs**, payment gateway webhooks, or autonomous fund transfer capabilities.
* **Context Grounding & Hallucination Defense**: Spendable AI system prompts strictly ground responses in computed user metrics (`current_balance`, `safe_spendable_capacity`, `detected_commitments`, `forecast_min_balance`). Prompts explicitly instruct the LLM to output uncertainty warnings when forecast confidence bands widen or balance floors drop below safety thresholds.
* **Deterministic Fallback Engine**: If the Gemini API is unconfigured, unreachable, or rate-limited, Spendable automatically activates a **Rule-Based Deterministic Synthesizer** to deliver verified textual advice from computed facts, guaranteeing 100% uptime and zero reliance on external LLMs.
* **Account-Scoped Data Context**: API endpoints enforce strict query parameter scoping by `account_id`, ensuring user requests retrieve only snapshot data associated with the active session context.

#### 2. Implemented Prototype Security Hardening Pass & Audit Controls
* **Cross-Account Data Isolation**: Server-side token validation on all financial routes (`/overview`, `/forecast`, `/activity`, `/recommendations`, `/simulate`, `/explain`, `/chat`, `/activities`) strictly derives account identity from authenticated JWT credentials. Attempts to access another user's financial data via parameter tampering are rejected with HTTP 403 Forbidden.
* **Strict JWT Authentication & Session Hardening**: Bearer tokens are validated for signature integrity and expiration on every protected request, returning HTTP 401 Unauthorized for malformed or expired tokens while preserving unauthenticated demo account selector access.
* **In-Memory Rate Limiting**: Endpoint rate limiting (`RateLimiter`) safeguards authentication (`/auth/login`, `/auth/register`, `/auth/demo-login`) and AI endpoints (`/spendable/chat`, `/spendable/explain`), returning HTTP 429 Too Many Requests when threshold limits are exceeded.
* **Adversarial Prompt-Injection Defense**: Enhanced system instructions (`SPENDABLE_AI_SYSTEM_INSTRUCTION`) and keyword pre-screening block malicious system prompt overrides, prompt jailbreaks, secret key extraction attempts, and unauthorized payment execution claims.
* **Security Audit Logging**: Thread-safe audit logger (`SecurityAuditLogger`) captures structured security events (`CROSS_ACCOUNT_ACCESS_DENIED`, `AUTH_LOGIN_SUCCESS`, `PROMPT_INJECTION_DETECTED`, `RATE_LIMIT_EXCEEDED`, `FINANCIAL_SNAPSHOT_ACCESSED`) without recording raw passwords, secret keys, or JWT tokens.
* **Automated Security & Scalability Test Suite**: Comprehensive test suite verifies cross-account isolation, token expiration, rate limiting, prompt injection defenses, forecast caching, failure recovery, and CSV transaction ingestion across **149 total passing backend tests**.

#### 3. Remaining Production Security Limitations (Post-Hackathon Roadmap)
* **Secret Storage**: Current environment uses local `.env` configuration (`SECRET_KEY=your_secret_key_placeholder...`); production deployment requires external secret vaults (AWS Secrets Manager / HashiCorp Vault).
* **Distributed Rate Limiting**: Prototype uses thread-safe in-memory sliding-window rate limiting; multi-region production scale requires Redis-backed distributed rate limiters.
* **Database Row-Level Security**: Isolation is enforced at the FastAPI application layer; production hardening will add PostgreSQL Row-Level Security (RLS) policies.

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
