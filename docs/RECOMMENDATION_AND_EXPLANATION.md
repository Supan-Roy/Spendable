# Stage 6 — Recommendation + Gemini Explanation Engine

## Core Architecture & Responsibility Separation

```
           Spendable Engine (Stage 4)
                      │
                      ▼
          Scenario Simulation (Stage 5)
                      │
                      ▼
   ┌─────────────────────────────────────┐
   │ Deterministic Recommendation Engine │  <-- SOURCE OF TRUTH (Part A)
   └──────────────────┬──────────────────┘
                      │
                      ▼
         Facts-Only ExplanationContext
                      │
                      ▼
   ┌─────────────────────────────────────┐
   │       Gemini Explanation Layer      │  <-- EXPLANATION ONLY (Parts B & C)
   │     (with Deterministic Fallback)   │
   └─────────────────────────────────────┘
```

The system enforces strict separation between **calculation/decision logic** (handled by deterministic code) and **natural language explanation** (handled by Gemini).

### Key Constraints:
- **Gemini NEVER calculates**: Spendable amounts, balances, minimum trajectories, or reserve buffers are ALREADY calculated by backend code before Gemini is invoked.
- **Gemini NEVER invents**: Cannot create fake commitments, fake income, fake balances, or unobserved transactions.
- **Gemini NEVER advises**: Does not make creditworthiness decisions, recommend loans/investments, or claim guaranteed affordability.
- **Deterministic Fallback**: If Gemini API key is missing or call fails, returns a deterministic fallback explanation ensuring 100% service uptime.

---

## 1. Part A — Deterministic Recommendation Engine (`backend/app/recommendation/`)

### Recommendation Types & Triggers:

| Recommendation Type | Priority Level | Triggering Objective Condition | Actionable Message Example |
| :--- | :---: | :--- | :--- |
| `LIQUIDITY_WARNING` | `CRITICAL` | `liquidity_state == PRESSURED` | *"Your projected balance may come under pressure within the next 30 days."* |
| `UPCOMING_COMMITMENTS` | `WARNING` / `INFO` | `upcoming_commitments > 0` | *"You have ৳15,000.00 in detected recurring commitments over the next 30 days."* |
| `SPENDING_CAUTION` | `WARNING` | `spendable_amount < 0.25 * current_balance` | *"Your estimated spendable amount is restricted to ৳9,200.00."* |
| `INCOME_IRREGULARITY` | `INFO` | Income/spending volatility addon active in safety reserve | *"Your recent cash flow has shown variability, so your safety buffer has been expanded."* |
| `FORECAST_PRESSURE` | `WARNING` | $R_{\text{safe}} \le B_{\min\_30\text{d}} < 1.5 R_{\text{safe}}$ | *"Your forecasted minimum balance of ৳8,500.00 is close to your safety threshold."* |
| `POSITIVE_LIQUIDITY` | `INFO` | `liquidity_state == HEALTHY` and $\text{Spendable} \ge 0.50 B_0$ | *"You have ৳25,000.00 in safe spendable capacity available."* |
| `SCENARIO_INSIGHT` | `WARNING` / `INFO` | `ScenarioResult` present | *"Simulating 'Spend ৳5,000' reduces your spendable amount by ৳5,000."* |

---

## 2. Part B — Facts-Only ExplanationContext (`backend/app/explanation/schema.py`)

Gemini receives only factual data fields:

```json
{
  "user_id": "ACC-0272",
  "snapshot_time": "2026-01-31T08:00:09+00:00",
  "current_balance": 160818.26,
  "spendable_amount": 92070.82,
  "protected_amount": 68747.44,
  "planning_horizon_days": 30,
  "expected_inflow": 104243.38,
  "expected_outflow": 71895.90,
  "upcoming_commitments": 15000.00,
  "forecasted_minimum_balance": 99084.51,
  "safety_reserve": 7013.71,
  "liquidity_state": "HEALTHY",
  "recommendations": [...],
  "scenario": {...},
  "limitations": [
    "Based strictly on observed account activity up to snapshot time T.",
    "Does not include unobserved bank accounts, physical cash, external wallets, or unrecorded financial liabilities."
  ]
}
```

---

## 3. Part C — Gemini System Instruction & Responsible AI Safeguards

### System Instruction Principles:
1. Explain provided financial facts clearly in human-readable language.
2. NEVER recalculate values.
3. NEVER invent fake transactions or unobserved income.
4. NEVER claim certainty or guaranteed affordability.
5. ALWAYS use Bangladeshi Taka symbol (৳).
6. Return structured JSON matching `GeminiExplanationResponse`.

---

## 4. How to Reproduce

```bash
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests
.\venv\Scripts\python.exe -m app.explanation.cli --output-report reports/recommendation_explanation_evaluation.json
```
