# Spendable — Stage 2: Recurring Payment & Financial Commitment Detection

## 1. Overview & Core Objective

The **Recurring Payment & Financial Commitment Detector** identifies repeating financial obligations (rent, utility bills, subscriptions, salary, loan EMIs, education fees, family support) using **only** observable transaction histories up to snapshot cutoff $T$ ($t \le T$).

### Core System Principles
1. **No Ground-Truth Leakage**: Planted recurring rules, persona allocations, and future outcome labels are strictly isolated. Ground truth is used **only** during offline performance evaluation.
2. **Strict Point-in-Time Cutoff**: Detector evaluates transactions where `timestamp <= snapshot_time`. Transactions occurring after $T$ are strictly excluded.
3. **Interpretability & Explainability**: Every detected commitment produces structured sub-score evidence explaining why it was classified as recurring.
4. **Non-Binary Categorical Confidence**: Classifies commitments as `STRONG`, `MODERATE`, or `INSUFFICIENT_EVIDENCE` rather than binary `true/false`.

---

## 2. Detection Algorithm & Evidence Scoring

Candidate transaction streams are grouped by:
- **Primary**: `(account_id, "COUNTERPARTY", counterparty_name, category)` when an informative merchant name is present.
- **Fallback**: `(account_id, "CATEGORY", category, category)` when counterparty info is absent.

### Sub-Score Formulation

$$\text{Confidence Score} = \min\left(1.0, \left(w_1 S_{\text{interval}} + w_2 S_{\text{amount}} + w_3 S_{\text{count}} + w_4 S_{\text{recency}}\right) \times \text{CategoryBoost}\right)$$

| Component Score | Weight | Formula / Description |
| :--- | :--- | :--- |
| **Interval Consistency ($S_{\text{interval}}$)** | `0.35` | Measures interval regularity against standard periodicity bands (`WEEKLY`: 7d, `BIWEEKLY`: 14d, `MONTHLY`: 30d, `QUARTERLY`: 90d, `ANNUAL`: 365d). Bounded in `[0, 1]`. |
| **Amount Consistency ($S_{\text{amount}}$)** | `0.30` | `1.0 - 1.5 * (std_amount / mean_amount)`. Penalizes high amount variability while accommodating minor bill fluctuations. |
| **Occurrence Count ($S_{\text{count}}$)** | `0.20` | `min(1.0, count / 8.0)`. Requires $\ge 3$ occurrences for candidate evaluation. |
| **Recency Score ($S_{\text{recency}}$)** | `0.15` | `1.0 - (recency_days / expected_window)`. Penalizes stale or inactive commitments. |
| **Category Domain Boost** | Multiplier | `1.1x` prior boost for core commitment categories (`HOUSING`, `UTILITIES`, `TELECOM`, `DEBT_PAYMENT`, `SOFTWARE`, `FITNESS`, `FAMILY_SUPPORT`, `INCOME`, `SALARY`, `RENT`). |

---

## 3. Threshold Configuration & Categorical Statuses

Configured via `DetectionConfig`:

| Threshold Name | Value | Meaning |
| :--- | :--- | :--- |
| `min_occurrences` | `3` | Minimum observations required before declaring a commitment |
| `strong_threshold` | `0.70` | Confidence score $\ge 0.70 \rightarrow \mathbf{\text{STRONG}}$ commitment |
| `moderate_threshold` | `0.45` | $0.45 \le \text{Confidence score} < 0.70 \rightarrow \mathbf{\text{MODERATE}}$ commitment |
| Below `0.45` or $<3$ obs | `< 0.45` | $\mathbf{\text{INSUFFICIENT\_EVIDENCE}}$ |

---

## 4. Offline Ground-Truth Evaluation Results

Evaluated at snapshot cutoff $T = \text{2026-10-01}$ across 500 synthetic user accounts split into user-level partitions.

| Split | Users | GT Rules | Detected | TP | FP | FN | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | 350 | 1,485 | 2,625 | 1,476 | 1,149 | 9 | **0.5623** | **0.9939** | **0.7182** |
| **VALIDATION** | 75 | 360 | 611 | 360 | 251 | 0 | **0.5892** | **1.0000** | **0.7415** |
| **TEST** | 75 | 363 | 638 | 362 | 276 | 1 | **0.5674** | **0.9972** | **0.7233** |

### Key Takeaways:
- **Zero Overfitting**: Metrics on `VALIDATION` (F1=0.7415) and `TEST` (F1=0.7233) closely align with `TRAIN` (F1=0.7182).
- **Near-Perfect Recall**: $>99.39\%$ recall across all splits (only 1 missed rule on TEST out of 363).
- **False Positives Analysis**: False positives consist of frequent non-commitment merchant visits (e.g. repeated grocery or coffee purchases at the same venue). These represent real recurring user spending behavior that can be optionally filtered by category or user preference.

---

## 5. Output Schema Example

```json
{
  "commitment_id": "comm_8f3a91b2c4e5",
  "user_id": "ACC-0001",
  "counterparty_name": "Dotlines Fiber Internet",
  "category": "UTILITIES",
  "activity_type": "UTILITY_BILL",
  "direction": "OUTFLOW",
  "expected_amount": 2916.0,
  "recurrence_interval": "MONTHLY",
  "median_interval_days": 30.0,
  "next_expected_date": "2026-10-10",
  "amount_variability": 0.0,
  "occurrence_count": 9,
  "confidence_score": 0.945,
  "detection_status": "STRONG",
  "evidence": {
    "occurrences": 9,
    "median_interval_days": 30.0,
    "mean_interval_days": 30.12,
    "std_interval_days": 0.35,
    "interval_cv": 0.0116,
    "mean_amount": 2916.0,
    "median_amount": 2916.0,
    "std_amount": 0.0,
    "amount_cv": 0.0,
    "recency_days": 21.0,
    "active_duration_days": 241.0,
    "interval_consistency_score": 0.985,
    "amount_consistency_score": 1.0,
    "recency_score": 0.5625,
    "count_score": 1.0
  }
}
```

---

## 6. Execution Commands

### Run Full Evaluation CLI
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m app.recurring.cli --dataset-dir data/ --snapshot-date 2026-10-01
```

### Run Pytest Test Suite
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\pytest.exe backend/tests/test_recurring_detector.py -v
```
