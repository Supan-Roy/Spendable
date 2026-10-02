# Spendable — Feature Catalog & Domain Feature Specifications

## 1. Overview & Architectural Principles

Spendable relies on point-in-time financial feature engineering to estimate liquidity runway and safe spendable capacity.

### Strict Point-in-Time Non-Leakage Invariant
Every feature vector evaluated at snapshot timestamp $T$ MUST satisfy:
$$\text{Feature}(T) = f\big(\{ \text{Activity}_i \mid \text{timestamp}_i \le T \}\big)$$

1. **Observable Facts Only**: Input features are constructed exclusively from observable customer account transaction activity occurring at or before snapshot time $T$.
2. **Zero Future Contamination**: Transactions occurring after $T$ ($t > T$) are strictly excluded from feature computation.
3. **Hidden Ground Truth Isolation**: Internal generator state (persona type, planted recurring rule IDs, drift milestone offsets) is excluded from input feature matrices. Ground truth future outcomes are used exclusively as offline evaluation targets.
4. **User-Level Partitioning**: Preprocessing and feature matrices are isolated across `TRAIN` (70%), `VALIDATION` (15%), and `TEST` (15%) user partitions without cross-user leakage.

---

## 2. Feature Catalog Specifications

### A. Current Liquidity Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `current_balance` | `float` | `BDT` | snapshot | Latest observed account balance at snapshot timestamp $T$. | LOW | Baseline liquidity anchor for runway estimation. |
| `balance_min_7d` | `float` | `BDT` | 7d | Minimum balance observed in $[T - 7\text{d}, T]$. | LOW | Short-term liquidity drawdown floor. |
| `balance_min_14d` | `float` | `BDT` | 14d | Minimum balance observed in $[T - 14\text{d}, T]$. | LOW | Biweekly liquidity drawdown floor. |
| `balance_min_30d` | `float` | `BDT` | 30d | Minimum balance observed in $[T - 30\text{d}, T]$. | LOW | Monthly liquidity drawdown floor. |
| `balance_max_30d` | `float` | `BDT` | 30d | Maximum balance observed in $[T - 30\text{d}, T]$. | LOW | Peak account liquidity tracking. |
| `balance_mean_30d` | `float` | `BDT` | 30d | Mean account balance across transactions in $[T - 30\text{d}, T]$. | LOW | Rolling average liquidity level. |
| `balance_std_30d` | `float` | `BDT` | 30d | Standard deviation of account balance in $[T - 30\text{d}, T]$. | LOW | Account balance stability & volatility. |
| `balance_change_7d` | `float` | `BDT` | 7d | Absolute balance change over past 7 days (`balance(T) - balance(T-7d)`). | LOW | Short-term balance trajectory velocity. |
| `balance_change_30d` | `float` | `BDT` | 30d | Absolute balance change over past 30 days (`balance(T) - balance(T-30d)`). | LOW | Monthly balance trajectory velocity. |

---

### B. Inflow Behavior Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `total_inflow_7d` | `float` | `BDT` | 7d | Sum of monetary inflows received in $[T - 7\text{d}, T]$. | LOW | Recent 7-day inflow volume. |
| `total_inflow_14d` | `float` | `BDT` | 14d | Sum of monetary inflows received in $[T - 14\text{d}, T]$. | LOW | Biweekly inflow volume. |
| `total_inflow_30d` | `float` | `BDT` | 30d | Sum of monetary inflows received in $[T - 30\text{d}, T]$. | LOW | Monthly inflow capacity. |
| `inflow_count_30d` | `int` | `count` | 30d | Count of inflow transactions in $[T - 30\text{d}, T]$. | LOW | Inflow frequency & multi-source income detection. |
| `avg_inflow_amount_30d` | `float` | `BDT` | 30d | Mean inflow transaction amount in $[T - 30\text{d}, T]$. | LOW | Typical incoming paycheck/payout size. |
| `days_since_last_inflow` | `float` | `days` | historical | Days elapsed between most recent inflow and snapshot $T$. | LOW | Paycheck cycle proximity & recency. |
| `inflow_volatility_30d` | `float` | `BDT` | 30d | Standard deviation of inflow amounts in $[T - 30\text{d}, T]$. | LOW | Salary stability vs freelance variability. |

---

### C. Outflow Behavior Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `total_outflow_7d` | `float` | `BDT` | 7d | Sum of monetary outflows spent in $[T - 7\text{d}, T]$. | LOW | Recent 7-day spending volume. |
| `total_outflow_14d` | `float` | `BDT` | 14d | Sum of monetary outflows spent in $[T - 14\text{d}, T]$. | LOW | Biweekly spending volume. |
| `total_outflow_30d` | `float` | `BDT` | 30d | Sum of monetary outflows spent in $[T - 30\text{d}, T]$. | LOW | Monthly spending volume. |
| `outflow_count_30d` | `int` | `count` | 30d | Count of outflow transactions in $[T - 30\text{d}, T]$. | LOW | Monthly transaction activity frequency. |
| `avg_outflow_amount_30d` | `float` | `BDT` | 30d | Mean outflow transaction amount in $[T - 30\text{d}, T]$. | LOW | Average transaction ticket size. |
| `median_outflow_amount_30d` | `float` | `BDT` | 30d | Median outflow transaction amount in $[T - 30\text{d}, T]$. | LOW | Robust median ticket size. |
| `days_since_last_outflow` | `float` | `days` | historical | Days elapsed between most recent outflow and snapshot $T$. | LOW | Spending recency. |
| `spending_volatility_30d` | `float` | `BDT` | 30d | Standard deviation of outflow transaction amounts in $[T - 30\text{d}, T]$. | LOW | Outflow ticket size variability. |

---

### D. Cash Flow Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `net_cash_flow_7d` | `float` | `BDT` | 7d | Net cash flow (`inflow_7d - outflow_7d`) in $[T - 7\text{d}, T]$. | LOW | Short-term net accumulation. |
| `net_cash_flow_14d` | `float` | `BDT` | 14d | Net cash flow (`inflow_14d - outflow_14d`) in $[T - 14\text{d}, T]$. | LOW | Biweekly net accumulation. |
| `net_cash_flow_30d` | `float` | `BDT` | 30d | Net cash flow (`inflow_30d - outflow_30d`) in $[T - 30\text{d}, T]$. | LOW | Monthly net accumulation. |
| `inflow_outflow_ratio_30d` | `float` | `ratio` | 30d | Ratio of total inflow to total outflow (`inflow_30d / (outflow_30d + 1e-5)`). | LOW | Financial coverage ratio. |
| `avg_daily_net_flow_30d` | `float` | `BDT` | 30d | Average daily net cash flow (`net_cash_flow_30d / 30.0`). | LOW | Daily net burn / accumulation rate. |

---

### E. Spending Behavior & Concentration Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `avg_transaction_amount_30d` | `float` | `BDT` | 30d | Mean of all transactions (inflows + outflows) in $[T - 30\text{d}, T]$. | LOW | Overall account transaction size. |
| `median_transaction_amount_30d` | `float` | `BDT` | 30d | Median of all transactions in $[T - 30\text{d}, T]$. | LOW | Overall account median size. |
| `transaction_frequency_30d` | `float` | `count/day` | 30d | Daily transaction frequency (`total_txns_30d / 30.0`). | LOW | Activity velocity. |
| `essential_spending_share_30d` | `float` | `ratio` | 30d | Outflow share spent on HOUSING, UTILITIES, and TELECOM. | LOW | Fixed obligation commitment ratio. |
| `discretionary_spending_share_30d` | `float` | `ratio` | 30d | Outflow share spent on DINING, GROCERIES, SHOPPING, and ENTERTAINMENT. | LOW | Discretionary spending flexibility. |
| `category_concentration_index_30d` | `float` | `index` | 30d | Herfindahl-Hirschman Index ($\sum s_i^2$) of 30d category outflow shares. | LOW | Spending category diversification vs concentration. |

---

### F. Balance Pressure Features

| Feature Name | Type | Unit | Window | Description | Leakage Risk | Intended Downstream Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `low_balance_days_ratio_30d` | `float` | `ratio` | 30d | Fraction of 30d transactions where `balance_after < ৳1,000.00`. | LOW | Liquidity stress exposure ratio. |
| `drawdown_from_recent_max_30d` | `float` | `ratio` | 30d | Balance drawdown from 30d maximum (`(bal_max_30d - current_bal) / bal_max_30d`). | LOW | Peak-to-current balance depletion ratio. |
| `recent_balance_trend_slope` | `float` | `slope` | 30d | Linear regression slope of balance vs day offset in $[T - 30\text{d}, T]$. | LOW | Balance trajectory direction and velocity. |

---

## 3. Offline Evaluation Targets (Ground Truth Layer)

The following targets are evaluated from transactions occurring AFTER snapshot timestamp $T$ ($t > T$) for offline evaluation ONLY:

| Target Name | Type | Window | Description |
| :--- | :--- | :--- | :--- |
| `target_future_min_balance_7d` | `float` | $[T+1\text{s}, T+7\text{d}]$ | Minimum account balance reached over next 7 days. |
| `target_future_min_balance_14d` | `float` | $[T+1\text{s}, T+14\text{d}]$ | Minimum account balance reached over next 14 days. |
| `target_future_min_balance_30d` | `float` | $[T+1\text{s}, T+30\text{d}]$ | Minimum account balance reached over next 30 days. |
| `target_liquidity_shortfall_30d` | `int` (0/1) | $[T+1\text{s}, T+30\text{d}]$ | Binary flag: `1` if `target_future_min_balance_30d < ৳1,000.00`, else `0`. |
| `target_future_net_cash_flow_30d` | `float` | $[T+1\text{s}, T+30\text{d}]$ | Net cash flow over next 30 days (`future_inflows - future_outflows`). |
