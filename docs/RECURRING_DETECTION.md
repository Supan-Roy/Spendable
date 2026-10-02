# Spendable — Stage 2: Refined Recurring Commitment & Income Detection

## 1. Overview & Problem Diagnosis

In the initial baseline detector, **1,148 false positives** were observed across the 350 `TRAIN` user accounts. Detailed error analysis identified two major root causes:
1. **Habitual Spending vs Commitment Confusion**: Generic discretionary purchases (`DINING`, `SHOPPING`, `TRANSPORT`, `GROCERIES`) without a specific merchant name were grouped together across different vendors, turning routine habit spending into artificial "recurring commitments".
2. **Inflow vs Outflow Mismatch**: Recurring income streams (`FREELANCE_INCOME`, `SALARY`) were evaluated against outflow financial obligations, creating 88 false positives.

### Core Architectural Refinements
1. **Commitment Likelihood Score ($S_{\text{commitment}}$)**: Formulated from counterparty specificity, interval periodicity, amount consistency, and category prior to distinguish contractual obligations from habit spending.
2. **Non-Grouping of Generic Discretionary Spending**: Skips grouping generic transactions without a specific merchant name.
3. **Directional Semantics Isolation**: Separates `OUTFLOW` financial commitments (Rent, Utilities, Telecom, Loans) from `INFLOW` income streams (Salary, Freelance).

---

## 2. Refined Detection Algorithm & Evidence Scoring

Candidate transaction streams are grouped by:
- **Primary**: `(account_id, "COUNTERPARTY", counterparty_name, category, direction)` when an informative merchant name is present.
- **Fallback**: `(account_id, "CATEGORY", category, category, direction)` when counterparty info is absent (skipping discretionary categories without counterparty).

### Sub-Score Formulation

$$\text{Commitment Likelihood Score} = \min\left(1.0, \left(w_1 S_{\text{interval}} + w_2 S_{\text{amount}} + w_3 S_{\text{count}} + w_4 S_{\text{recency}}\right) \times S_{\text{counterparty}} \times \text{CategoryPrior}\right)$$

| Component Score | Weight / Multiplier | Formula / Description |
| :--- | :--- | :--- |
| **Interval Consistency ($S_{\text{interval}}$)** | `0.35` | Measures interval regularity against standard periodicity bands (`WEEKLY`: 7d, `BIWEEKLY`: 14d, `MONTHLY`: 30d, `QUARTERLY`: 90d, `ANNUAL`: 365d). Bounded in `[0, 1]`. |
| **Amount Consistency ($S_{\text{amount}}$)** | `0.30` | `1.0 - 1.5 * (std_amount / mean_amount)`. Penalizes high amount variability while accommodating minor bill fluctuations. |
| **Occurrence Count ($S_{\text{count}}$)** | `0.20` | `min(1.0, count / 8.0)`. Requires $\ge 3$ occurrences for candidate evaluation. |
| **Recency Score ($S_{\text{recency}}$)** | `0.15` | `1.0 - (recency_days / expected_window)`. Penalizes stale or inactive commitments. |
| **Counterparty Score ($S_{\text{counterparty}}$)** | `1.0x` (Named) / `0.5x` (Category) | Specific merchant name provides strong commitment evidence. |
| **Category Domain Prior** | `1.1x` (Contractual) / `0.6x` (Discretionary) | `1.1x` boost for contractual categories (`HOUSING`, `UTILITIES`, `TELECOM`, `DEBT_PAYMENT`, `SOFTWARE`, `FITNESS`, `FAMILY_SUPPORT`, `EDUCATION`, `INSURANCE`, `RENT`). `0.6x` for discretionary spending. |

---

## 3. Threshold Configuration & Categorical Statuses

Configured via `DetectionConfig`:

| Threshold Name | Value | Meaning |
| :--- | :--- | :--- |
| `min_occurrences` | `3` | Minimum observations required before declaring a commitment |
| `strong_threshold` | `0.70` | Commitment Likelihood $\ge 0.70 \rightarrow \mathbf{\text{STRONG}}$ commitment |
| `moderate_threshold` | `0.45` | $0.45 \le \text{Commitment Likelihood} < 0.70 \rightarrow \mathbf{\text{MODERATE}}$ commitment |
| Below `0.45` or $<3$ obs | `< 0.45` | $\mathbf{\text{INSUFFICIENT\_EVIDENCE}}$ |

---

## 4. Final Evaluation Results Across Dataset Splits

Evaluated at snapshot cutoff $T = \text{2026-10-01}$ across 500 synthetic user accounts split into user-level partitions (`direction_filter="OUTFLOW"`).

| Split | Users | GT Rules | Detected | TP | FP | FN | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | 350 | 1,204 | 1,198 | 1,194 | 4 | 10 | **0.9967** | **0.9917** | **0.9942** |
| **VALIDATION** | 75 | 297 | 297 | 297 | 0 | 0 | **1.0000** | **1.0000** | **1.0000** |
| **TEST** | 75 | 300 | 298 | 298 | 0 | 2 | **1.0000** | **0.9933** | **0.9967** |

### False Positive Reduction
- **Initial Baseline False Positives**: `1,148` (TRAIN)
- **Refined Detector False Positives**: `4` (TRAIN), `0` (VALIDATION), `0` (TEST)
- **Precision Improvement**: Increased from `56.23%` to **`99.67%`** (TRAIN) and **`100.00%`** (VALIDATION & TEST).

---

## 5. TRAIN Category-Level Evaluation Breakdown

| Category | GT Count | Detected Count | TP | FP | FN | Precision | Recall |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DEBT_PAYMENT` | 50 | 50 | 50 | 0 | 0 | **1.0000** | **1.0000** |
| `ENTERTAINMENT` | 100 | 101 | 100 | 1 | 0 | **0.9901** | **1.0000** |
| `FAMILY_SUPPORT` | 61 | 61 | 61 | 0 | 0 | **1.0000** | **1.0000** |
| `FITNESS` | 50 | 50 | 50 | 0 | 0 | **1.0000** | **1.0000** |
| `HOUSING` | 350 | 349 | 348 | 1 | 2 | **0.9971** | **0.9943** |
| `SOFTWARE` | 50 | 50 | 50 | 0 | 0 | **1.0000** | **1.0000** |
| `TELECOM` | 123 | 122 | 122 | 0 | 1 | **1.0000** | **0.9919** |
| `UTILITIES` | 420 | 415 | 413 | 2 | 7 | **0.9952** | **0.9833** |

---

## 6. Execution Commands

### Run Full Evaluation CLI
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m app.recurring.cli --dataset-dir data/ --snapshot-date 2026-10-01 --direction OUTFLOW
```

### Run Pytest Test Suite
```powershell
$env:PYTHONPATH="backend"; .\venv\Scripts\pytest.exe backend/tests/test_recurring_detector.py -v
```
