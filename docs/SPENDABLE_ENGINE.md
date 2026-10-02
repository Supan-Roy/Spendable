# Stage 4 — Spendable Financial Intelligence Engine

## Core Product Proposition

> *"Your balance tells you how much money you have. Spendable tells you how much you can realistically afford to spend."*

The **Spendable Engine** is the core financial intelligence differentiator of the Spendable application. It computes a safe, behavior-aware spendable capacity ($\text{Spendable Amount}$) strictly traceable to observable transaction history, detected recurring financial commitments, multi-horizon cash-flow forecasts, and an adaptive safety reserve buffer ($R_{\text{safe}}$).

---

## 1. Mathematical Methodology & Candidate Formulations

### Candidate A: Non-Double-Counting Protected Requirement (Selected & Recommended)

To prevent subtracting recurring commitments twice when they are already reflected in model-forecasted balance drawdowns, Candidate A defines:

$$\text{Forecasted Drawdown}_{30\text{d}} = \max\left(0, B_0 - B_{\min\_30\text{d}}\right)$$

$$\text{Protected Requirement} = \max\left(C_{\text{commitments\_30d}}, \text{Forecasted Drawdown}_{30\text{d}}\right) + R_{\text{safe}}$$

$$\text{Spendable Amount} = \max\left(0.0, B_0 - \text{Protected Requirement}\right)$$

where:
- $B_0$: Observed account balance at snapshot time $T$.
- $C_{\text{commitments\_30d}}$: Sum of detected recurring financial commitments due over the next 30 days.
- $B_{\min\_30\text{d}}$: Model-predicted 30-day minimum account balance trajectory.
- $R_{\text{safe}}$: Adaptive safety reserve buffer.

### Alternative Candidate Formulations Evaluated:

- **Candidate B (Forecast-Aware Trajectory Buffer)**:
  $$\text{Spendable Amount} = \max\left(0.0, B_{\min\_30\text{d}} - R_{\text{safe}}\right)$$
  *Focuses purely on the model's forecasted minimum balance, ignoring commitment breakdown details.*

- **Candidate C (Commitment-Aware Direct Cash Buffer)**:
  $$\text{Spendable Amount} = \max\left(0.0, B_0 - C_{\text{commitments\_30d}} - R_{\text{safe}}\right)$$
  *Subtracts recurring commitments and reserve directly from current balance, ignoring predicted cash flow trajectories and discretionary spending velocity.*

---

## 2. Adaptive Safety Reserve ($R_{\text{safe}}$)

The safety reserve is behavior-driven and scales dynamically with observed user risk factors:

$$R_{\text{safe}} = \min\left(B_0, \max\left(\text{MinReserve}, \text{BaselineBuffer} + \text{Addon}_{\text{volatility}} + \text{Addon}_{\text{income}} + \text{Addon}_{\text{commitment}}\right)\right)$$

1. **Baseline Buffer**: 7 days of cover based on 30-day average daily outflow ($\text{daily\_outflow} \times 7$), minimum floor of ৳3,000 BDT.
2. **Spending Volatility Addon**: Scales up to 50% of baseline buffer for high spending coefficient of variation ($CV_{\text{outflow}} > 0.3$).
3. **Income Irregularity Addon**: Scales up to 40% cushion for unstable or irregular income streams ($CV_{\text{income}} > 0.4$).
4. **Commitment Burden Addon**: Adds 15% of commitment obligation if commitments exceed 30% of current balance.

---

## 3. Categorical Liquidity States

The engine classifies account liquidity into three transparent states:

- **`HEALTHY`**: $B_{\min\_30\text{d}} \ge 1.5 \times R_{\text{safe}}$ and $\text{Spendable Amount} \ge 0.25 \times B_0$.
- **`WATCH`**: $R_{\text{safe}} \le B_{\min\_30\text{d}} < 1.5 \times R_{\text{safe}}$ or $0 < \text{Spendable Amount} < 0.25 \times B_0$.
- **`PRESSURED`**: $B_{\min\_30\text{d}} < R_{\text{safe}}$, $\text{Spendable Amount} == 0.0$, or $B_0 \le 0.0$.

---

## 4. Machine-Readable Explanation Factors

Each execution returns structured, machine-readable factor objects passed downstream to Gemini for natural language synthesis:

```json
[
  {
    "type": "UPCOMING_COMMITMENT",
    "impact": "NEGATIVE",
    "amount": 10000.0,
    "description": "৳10,000.00 reserved for detected recurring bills and commitments over 30 days."
  },
  {
    "type": "EXPECTED_INFLOW",
    "impact": "POSITIVE",
    "amount": 40000.0,
    "description": "৳40,000.00 projected incoming cash flow over next 30 days."
  },
  {
    "type": "SAFETY_BUFFER",
    "impact": "NEGATIVE",
    "amount": 5000.0,
    "description": "৳5,000.00 allocated to adaptive safety reserve buffer for unexpected expenses."
  }
]
```

---

## 5. Historical Backtest Results (10,981 Snapshots)

| Split | Total Snapshots | Candidate A Mean Spendable | Candidate A Breach Rate | Candidate B Breach Rate | Candidate C Breach Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **TRAIN** | 7,685 | ৳338,443.23 | 51.82% | 52.11% | 88.89% |
| **VALIDATION** | 1,647 | ৳367,971.49 | 52.09% | 52.46% | 89.50% |
| **TEST** | 1,649 | ৳325,967.26 | 51.18% | 51.55% | 89.02% |

*Candidate A achieved superior liquidity protection compared to Candidate C (which breached safety in 89% of cases by ignoring model drawdown predictions).*

---

## 6. How to Reproduce

```bash
$env:PYTHONPATH="backend"
.\venv\Scripts\python.exe -m app.engine.cli --output-report reports/spendable_engine_evaluation.json
.\venv\Scripts\pytest backend/tests
```
