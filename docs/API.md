# Stage 7 — FastAPI Product Integration Documentation

## Overview

The FastAPI backend exposes versioned product-oriented endpoints (`/api/v1/...`) enabling React frontend consumption of the Spendable financial intelligence pipeline:

- **Spendable Engine (Stage 4)**
- **Scenario Simulation Engine (Stage 5)**
- **Recommendation Engine (Stage 6)**
- **Gemini Explanation Layer (Stage 6)**

The FastAPI layer acts as an application orchestrator. All domain calculations remain isolated inside authoritative backend domain modules under `backend/app/engine/`, `backend/app/scenario/`, `backend/app/recommendation/`, and `backend/app/explanation/`.

---

## Endpoint Specification

### 1. GET `/api/v1/overview` (and `/api/v1/spendable/overview`)

Returns the main dashboard overview state.

**Query Parameters:**
- `user_id` (optional `str`): Filter by account identifier.
- `snapshot_time` (optional `str`): Point-in-time snapshot timestamp $T$.

**Response (`SpendableOverviewResponse`):**
```json
{
  "user_id": "ACC-0497",
  "snapshot_time": "2026-01-31T08:00:09+00:00",
  "current_balance": 59835.05,
  "spendable_amount": 22552.76,
  "protected_amount": 37282.29,
  "planning_horizon_days": 30,
  "liquidity_state": "HEALTHY",
  "expected_inflow": 40000.0,
  "expected_outflow": 25000.0,
  "upcoming_commitments": 10000.0,
  "forecasted_minimum_balance": 34284.50,
  "safety_reserve": 11731.74,
  "recommendations": [
    {
      "type": "INCOME_IRREGULARITY",
      "priority": "INFO",
      "title": "Adaptive Volatility Buffer Active",
      "message": "Your recent cash flow has shown variability, so your safety buffer has been expanded.",
      "supporting_amount": 5514.07,
      "supporting_metric": "volatility_addon",
      "reason": "Safety reserve includes an additional ৳5,514.07 buffer due to cash flow volatility.",
      "action": "Maintain liquidity buffer to cushion against income fluctuations."
    }
  ],
  "factors": [...],
  "explanation_summary": "You have ৳22,552.76 safely spendable out of your ৳59,835.05 account balance over the next 30 days."
}
```

---

### 2. GET `/api/v1/forecast` (and `/api/v1/spendable/forecast`)

Returns multi-horizon cash flow forecasts (7d, 14d, 30d) and 30-day daily projected balance trajectory.

**Response (`SpendableForecastResponse`):**
```json
{
  "user_id": "ACC-0497",
  "snapshot_time": "2026-01-31T08:00:09+00:00",
  "current_balance": 59835.05,
  "forecast_7d": {
    "horizon_days": 7,
    "expected_inflow": 10000.0,
    "expected_outflow": 5000.0,
    "expected_net_cash_flow": 5000.0,
    "projected_balance": 64835.05,
    "minimum_projected_balance": 55000.0,
    "liquidity_pressure_flag": false,
    "estimated_range_lower": 50000.0,
    "estimated_range_upper": 70000.0
  },
  "forecast_14d": { ... },
  "forecast_30d": { ... },
  "daily_trajectory": [ ... ],
  "safety_threshold_bdt": 15000.0
}
```

---

### 3. GET `/api/v1/activity` (and `/api/v1/spendable/activity`)

Returns recent observed transaction activity with pagination.

**Query Parameters:**
- `user_id` (optional `str`)
- `limit` (default: 50, max: 500)
- `offset` (default: 0)

---

### 4. GET `/api/v1/recommendations` (and `/api/v1/spendable/recommendations`)

Returns prioritized deterministic recommendations alongside Gemini explanation (or fallback).

---

### 5. POST `/api/v1/simulate` (and `/api/v1/spendable/simulate`)

Simulates a hypothetical scenario without mutating base state.

**Request Body (`ScenarioInput`):**
```json
{
  "scenario_type": "ONE_TIME_EXPENSE",
  "amount": 5000.0,
  "description": "Spend ৳5,000 today"
}
```

**Response (`ScenarioResult`):** Returns base spendable, scenario spendable, delta, and recalculated liquidity states.

---

### 6. POST `/api/v1/explain` (and `/api/v1/spendable/explain`)

Returns Gemini explanation response (or deterministic fallback).

---

## Local Startup Instructions

```bash
# Set PYTHONPATH and start uvicorn dev server
$env:PYTHONPATH="backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`
