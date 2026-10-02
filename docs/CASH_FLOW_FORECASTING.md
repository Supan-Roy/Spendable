# Spendable — Stage 3: Cash-Flow Forecasting & Short-Term Liquidity Trajectories

## 1. Core Objective & Architectural Overview

Stage 3 builds a practical, explainable, and leakage-safe cash-flow forecasting engine that answers:

> **"Given everything observable about a user up to snapshot time $T$, what is likely to happen to this user's balance over the next 7, 14, and 30 days?"**

The system forecasts:
- `future_min_balance_7d`, `future_min_balance_14d`, `future_min_balance_30d` (the primary target for Spendable safety margins).
- Expected cumulative inflows, outflows, and net cash flow across 7d, 14d, and 30d windows.
- 30-day continuous daily projected balance trajectory ($d \in [1, 30]$).
- Low-balance liquidity pressure anticipation flags (`minimum_projected_balance < 15,000 BDT`).

---

## 2. Model Architectures Implemented

1. **Baseline A — Rolling Average Baseline (`RollingAverageBaseline`)**:
   - Extrapolates rolling 30-day net cash flow rate ($r = \text{net\_cash\_flow\_30d} / 30.0$).
   - Projects $H$-day balance: $\text{bal}_H = \max(0, \text{current\_balance} + r \cdot H)$.
2. **Baseline B — Recurring Commitment Baseline (`RecurringCommitmentBaseline`)**:
   - Subtracts point-in-time detected recurring commitments ($t \le T$) due within horizon $H$.
3. **Supervised ML Model — Gradient Boosted Trees (`HistGradientBoostingRegressor`)**:
   - Multi-horizon estimator trained on 38 point-in-time snapshot features + 6 detected recurring commitment features.
   - Out-of-fold residual standard deviations provide prediction intervals (`estimated_range_lower`, `estimated_range_upper`).

---

## 3. Baseline vs ML Model Comparison (Validation Set)

Evaluated on 1,647 snapshots across 75 `VALIDATION` user accounts (fitted strictly on 7,685 `TRAIN` snapshots).

| Model Architecture | Horizon | MAE (BDT) | RMSE (BDT) | $R^2$ Score | Pressure F1 (30d) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rolling Average Baseline** | 7d | 16,972.14 | 33,429.98 | 0.9923 | - |
| **Rolling Average Baseline** | 14d | 22,148.81 | 35,123.09 | 0.9913 | - |
| **Rolling Average Baseline** | 30d | 28,418.56 | 41,137.53 | 0.9879 | 0.6577 |
| **Recurring Commitment Baseline** | 7d | 16,842.70 | 32,759.45 | 0.9926 | - |
| **Recurring Commitment Baseline** | 14d | 21,926.65 | 33,987.57 | 0.9919 | - |
| **Recurring Commitment Baseline** | 30d | 27,750.43 | 38,998.73 | 0.9891 | 0.6207 |
| **HistGradientBoosting ML** | 7d | **15,429.47** | **28,354.90** | **0.9944** | - |
| **HistGradientBoosting ML** | 14d | **15,655.88** | **27,274.81** | **0.9948** | - |
| **HistGradientBoosting ML** | 30d | **15,873.29** | **26,436.34** | **0.9950** | **0.8293** |

* **Selection Rationale**: The supervised `HistGradientBoostingRegressor` model reduces 30-day minimum balance prediction MAE from 28,418 BDT down to **15,873 BDT** (a **44.1% error reduction**) and increases 30-day Liquidity Pressure F1 from 0.6577 to **0.8293**.

---

## 4. Final Unbiased Test Set Evaluation

Evaluated on 1,649 snapshots across 75 `TEST` user accounts (completely un-tuned).

| Horizon | MAE (BDT) | RMSE (BDT) | $R^2$ Score | Pressure Precision | Pressure Recall | Pressure F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **7 Days** | **13,982.08** | 24,685.64 | 0.9946 | - | - | - |
| **14 Days** | **13,907.12** | 23,437.21 | 0.9951 | - | - | - |
| **30 Days** | **14,682.01** | 23,903.56 | 0.9948 | **0.9153** (91.53%) | **0.8244** (82.44%) | **0.8675** |

---

## 5. Persona Performance Breakdown (30-Day Minimum Balance)

| Persona Profile | Snapshots | MAE 30d (BDT) | RMSE 30d (BDT) | Pressure F1 | Behavior Characteristics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TIGHT_LIQUIDITY` | 374 | **5,720.32** | 8,947.49 | **0.9545** | Low balances, high pressure frequency $\rightarrow$ **Highest pressure anticipation F1 (0.9545)** |
| `SPENDING_DRIFT` | 220 | **11,610.09** | 17,956.51 | 0.0000 | Gradual expenditure acceleration |
| `STABLE` | 374 | **14,791.03** | 24,062.88 | 0.0000 | Predictable recurring salary and bills |
| `FINANCIAL_PRESSURE` | 110 | **15,744.92** | 22,239.99 | 0.0000 | Persistent deficit spending |
| `COMMITMENT_HEAVY` | 308 | **16,230.30** | 24,229.17 | 0.0000 | Fixed recurring commitment heavy profiles |
| `IRREGULAR_INCOME` | 263 | **27,582.89** | 38,486.29 | 0.2857 | High income volatility $\rightarrow$ Higher variance |

---

## 6. Top Feature Importances (Permutation Importance)

1. `current_balance` (`0.3567`): Primary anchor for future balance trajectory.
2. `balance_max_30d` (`0.2315`): Captures recent account liquidity peak scale.
3. `balance_min_30d` (`0.0207`): Historical minimum baseline indicator.
4. `balance_mean_30d` (`0.0167`): Rolling central tendency of account balance.
5. `balance_min_7d` (`0.0074`): Short-term recent minimum balance.
6. `recurring_outflow_30d` (`0.0011`): Detected upcoming commitments due over next month.

---

## 7. Execution Commands

### Run Full Evaluation CLI
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m app.forecasting.cli --dataset-dir data/ --safety-threshold 15000
```

### Run Pytest Suite
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\pytest.exe backend/tests/test_cash_flow_forecasting.py -v
```
