# Stage 7 — FastAPI Product Integration Documentation

## Overview

The FastAPI backend exposes versioned product-oriented endpoints (`/api/v1/...`) enabling React frontend consumption of the Spendable financial intelligence pipeline:

- **Spendable Engine (Stage 4)**
- **Scenario Simulation Engine (Stage 5)**
- **Recommendation Engine (Stage 6)**
- **Gemini Explanation & Spendable AI Layer (Stage 6)**

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
  "recommendations": [ ... ],
  "factors": [ ... ],
  "explanation_summary": "You have ৳22,552.76 safely spendable out of your ৳59,835.05 account balance over the next 30 days."
}
```

---

### 2. GET `/api/v1/forecast` (and `/api/v1/spendable/forecast`)

Returns multi-horizon cash flow forecasts (7d, 14d, 30d) and 30-day daily projected balance trajectory.

---

### 3. GET `/api/v1/activity` (and `/api/v1/spendable/activity`)

Returns recent observed transaction activity with pagination.

**Query Parameters:**
- `user_id` (optional `str`)
- `limit` (default: 50, max: 500)
- `offset` (default: 0)

---

### 4. POST `/api/v1/simulate` (and `/api/v1/spendable/simulate`)

Simulates a hypothetical scenario without mutating base state.

**Supported `scenario_type` Values:**
- `ONE_TIME_EXPENSE` (One-time expense deduction)
- `ADDITIONAL_INCOME` (One-time income inflow addition)
- `ADDITIONAL_COMMITMENT` (New recurring bill/rent obligation)
- `SPENDING_REDUCTION` (Percentage reduction in discretionary spending)
- `INCOME_DELAY` (Delayed income inflow)

**Request Body (`ScenarioInput`):**
```json
{
  "scenario_type": "ONE_TIME_EXPENSE",
  "amount": 5000.0,
  "description": "Spend ৳5,000 today"
}
```

**Response (`ScenarioResult`):**
```json
{
  "user_id": "acc_supan",
  "snapshot_time": "2026-10-03T17:30:00+00:00",
  "scenario_type": "ONE_TIME_EXPENSE",
  "scenario_description": "Spend ৳5,000 today",
  "base_spendable_amount": 22552.76,
  "scenario_spendable_amount": 17552.76,
  "spendable_delta": -5000.0,
  "base_current_balance": 59835.05,
  "scenario_current_balance": 54835.05,
  "base_forecasted_minimum_balance": 34284.50,
  "scenario_forecasted_minimum_balance": 29284.50,
  "base_safety_reserve": 11731.74,
  "scenario_safety_reserve": 11731.74,
  "base_liquidity_state": "HEALTHY",
  "scenario_liquidity_state": "HEALTHY"
}
```

---

### 5. POST `/api/v1/chat`

Conversational assistant endpoint powered by Spendable AI (Gemini SDK).

**Request Body (`ChatRequest`):**
```json
{
  "message": "Can I afford a ৳15,000 purchase right now?",
  "chat_history": [ ... ],
  "scenario_result": { ... }
}
```

**Response (`ChatResponse`):**
```json
{
  "reply": "Hello! I am **Spendable AI**. Based on your current balance of ৳59,835.05 and ৳10,000 upcoming bill commitments, your safe spendable capacity is ৳22,552.76. A ৳15,000 purchase is safely within your spendable margin!",
  "model_used": "gemini-2.5-flash",
  "is_fallback": false
}
```

---

### 6. POST `/api/v1/explain` (and `/api/v1/spendable/explain`)

Returns Gemini explanation response (or deterministic fallback).

---

## Local Startup Instructions

```bash
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`
