# Stage 5 — Scenario Simulation Engine

## Core Product Proposition

> *"What happens to my financial runway and safe spendable capacity if I change something?"*

The **Scenario Simulation Engine** (Stage 5) provides a thin, deterministic, non-mutating simulation wrapper around the authoritative **Spendable Engine** (Stage 4). It evaluates hypothetical financial choices ("what-if" scenarios) without modifying base financial states or introducing future transaction data leakage.

---

## 1. Supported Scenario Types & Transformations

| Scenario Type | User Form Label | Input Parameters | State Transformation Logic |
| :--- | :--- | :--- | :--- |
| `ONE_TIME_EXPENSE` | *"Spend money (One-time expense)"* | `amount` (BDT) | $B'_0 = \max(0, B_0 - \text{expense})$<br>$B'_{\min} = \max(0, B_{\min} - \text{expense})$ |
| `ADDITIONAL_INCOME` | *"Receive money (One-time inflow)"* | `amount` (BDT) | $B'_0 = B_0 + \text{income}$<br>$B'_{\min} = B_{\min} + \text{income}$<br>$\text{expected\_inflow}' = \text{expected\_inflow} + \text{income}$ |
| `ADDITIONAL_COMMITMENT` | *"Add commitment (Monthly bill/rent)"* | `amount` (BDT) | $C'_{\text{commitments}} = C_{\text{commitments}} + \text{amount}$ |
| `SPENDING_REDUCTION` | *"Reduce spending (%)"* | `percentage` (%) | $\text{outflow}' = \text{outflow} \times (1 - \frac{p}{100})$<br>$B'_{\min} = B_{\min} + \Delta_{\text{savings}}$ |
| `INCOME_DELAY` | *"Delay income (Amount)"* | `amount` (BDT) | $\text{expected\_inflow}' = \max(0, \text{expected\_inflow} - \text{delayed})$<br>$B'_{\min} = \max(0, B_{\min} - \text{delayed})$ |

---

## 2. Immutability & Non-Leakage Architecture

```
        Original Base Financial State (B_0, B_min, C_commitments)
                                  │
                                  ▼ [Deep Copy / Derivative Transformation]
                    Derived Hypothetical Scenario State
                                  │
                                  ▼
                      Authoritative Spendable Engine
                        (calculator.calculate)
                                  │
                                  ▼
                            ScenarioResult
```

1. **Zero Base Mutation**: Base snapshot features, detected commitments, and forecast outputs are deep-copied prior to modification.
2. **Point-in-Time Cutoff**: Operates strictly on features $\le T$ + explicit scenario parameter. Zero future leakage.

---

## 3. Multi-Metric Impact Dashboard Output

When a scenario is simulated, the backend produces a structured `ScenarioResult` payload containing full before-and-after financial metrics:

- `base_spendable_amount` vs `scenario_spendable_amount` (with `spendable_delta`)
- `base_current_balance` vs `scenario_current_balance`
- `base_forecasted_minimum_balance` vs `scenario_forecasted_minimum_balance`
- `base_safety_reserve` vs `scenario_safety_reserve`
- `base_liquidity_state` vs `scenario_liquidity_state`

This structured result feeds directly into the frontend **Scenario Impact Dashboard** and can be passed to **Spendable AI** for context-grounded conversational insights.

---

## 4. Financial Sanity & Monotonicity Laws

The `ScenarioValidator` enforces 10 mandatory financial sanity rules across all simulated scenarios:

1. **Spending More Monotonicity**: Spending $>0$ never increases spendable capacity.
2. **Income Increase Monotonicity**: Additional positive income never decreases spendable capacity under normal conditions.
3. **Commitment Monotonicity**: Additional obligation never increases spendable capacity.
4. **Spending Reduction Monotonicity**: Cutting spending never decreases spendable capacity under normal conditions.
5. **Base Immutability**: Base Spendable Output before and after simulation is bitwise identical.
6. **Zero Adjustment Identity**: Zero scenario adjustment returns exact baseline output.
7. **Over-Balance Expense Safety**: Expense > balance safely yields `spendable_amount = 0.0`.
8. **Recalculated Liquidity State**: Liquidity state is dynamically reclassified (`HEALTHY`, `WATCH`, `PRESSURED`).
9. **Deterministic Output**: Identical inputs yield identical outputs.
10. **Finite Bounded Numeric Safety**: No `NaN` or `Infinity`.

---

## 5. Evaluation Summary (700 Scenarios Tested)

- **Total Snapshots Evaluated**: 100
- **Total Scenarios Executed**: 700
- **Monotonicity Violations**: 0
- **Negative Spendable Violations**: 0
- **State Mutation Violations**: 0
- **Passed All Sanity Checks**: `True`

---

## 6. How to Reproduce

```bash
$env:PYTHONPATH="backend"
python -m pytest backend/tests
python -m app.scenario.cli --output-report reports/scenario_simulation_evaluation.json
```
