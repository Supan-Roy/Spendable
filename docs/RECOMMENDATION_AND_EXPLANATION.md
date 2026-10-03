# Stage 6 — Recommendation Engine & Spendable AI Layer

## Core Product Proposition

> *"Translate raw numbers into actionable advice and conversational financial intelligence."*

Stage 6 combines **Deterministic Prioritized Recommendations** with **Spendable AI** (Google Gemini LLM context injection). All financial calculations remain 100% code-enforced; Gemini is invoked exclusively to format conversational guidance and answer user questions without hallucinating money figures.

---

## 1. Spendable AI Conversational Chat Assistant (`/api/v1/chat`)

- **Persona Rule**: Identifies as *"Spendable AI, your personal financial liquidity assistant"*.
- **Scope Guardrails**: Strictly constrained to personal finance, liquidity management, spendable runway, recurring bill tracking, and scenario analysis. Polymorphic out-of-context requests (coding help, creative stories, non-financial trivia) are politely declined.
- **Context Injection**: Each chat turn receives a structured JSON payload containing:
  - Account Balance ($B_0$)
  - Safe Spendable Capacity ($\text{Spendable}$)
  - Protected Safety Reserve & Upcoming Bills
  - Active What-If Scenario Result (if attached from the Simulate tab)

---

## 2. Recommendation Engine Rules (`RecommendationEngine`)

Computes deterministic, prioritized recommendation cards across 5 financial rules:

| Rule ID | Category | Trigger Condition | Output Recommendation |
| :--- | :--- | :--- | :--- |
| `REC_LIQUIDITY_DEFICIT` | `HIGH_RISK` | $B_{\text{min, 30d}} < 0$ | *"Projected Deficit Alert: Deficit of ৳X expected on Date Y. Reserve cash immediately."* |
| `REC_COMMITMENT_COVERAGE` | `MEDIUM_RISK` | $\text{Spendable} < C_{\text{commitments}}$ | *"Commitment Protection Alert: Upcoming bills exceed uncommitted liquidity."* |
| `REC_VOLATILITY_EXPANSION` | `INFO` | $\sigma_{\text{outflow}} > \text{threshold}$ | *"Adaptive Safety Buffer Active: Reserved additional ৳X buffer due to cash flow fluctuations."* |
| `REC_SURPLUS_OPPORTUNITY` | `OPPORTUNITY` | $\text{Spendable} > \text{threshold}$ | *"Surplus Liquidity Detected: ৳X safely available for high-yield savings or debt reduction."* |
| `REC_SCENARIO_MUTATION` | `SIMULATION` | Scenario State Changed | *"Scenario Impact Alert: Simulated action shifts liquidity state to Pressured."* |

---

## 3. Fallback Synthesizer Architecture

If network access to Google Gemini API is unavailable or delayed:

1. The system captures the `GeminiExplanationResponse` exception.
2. A local **Deterministic Fallback Synthesizer** builds a clean, structured bullet-point response directly from the top recommendation items and `SpendableOutput` factors.
3. Sets `is_fallback: true` in the API payload so the UI gracefully displays context without failing.

---

## 4. How to Reproduce

```bash
$env:PYTHONPATH="backend"
python -m pytest backend/tests/test_recommendation_explanation.py
```
