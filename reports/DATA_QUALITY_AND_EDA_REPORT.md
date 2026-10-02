# Spendable — Data Quality & Exploratory Data Analysis (EDA) Report

**Generated Date (UTC)**: `2026-10-02T06:41:37.895901+00:00`  
**Overall Dataset Validation Status**: `WARNING`  
**Total Records**: `98884` | **Total Synthetic Users**: `500`  

---

## 1. Executive Summary & Quality Status

The synthetic dataset was subjected to automated validation and exploratory analysis conforming strictly to the [Spendable Financial Data Contract](file:///d:/Programs%20and%20Codes/Spendable/docs/FINANCIAL_DATA_CONTRACT.md).

- **Validation Result Summary**: `11 PASS`, `1 WARNING`, `0 FAIL`
- **Data Integrity Status**: All transaction IDs are 100% unique UUID v4 strings, monetary values are strictly positive (`amount > 0.00`), and timestamps are timezone-aware UTC representations.
- **Financial Progression Balance Integrity**: 100% of recorded `balance_after` values match exact reconstructed mathematical running balances (`Starting Balance + Inflows - Outflows`). Zero impossible negative balances detected.

---

## 2. Validation Suite Results

| Category | Check Name | Status | Description |
| :--- | :--- | :--- | :--- |
| `SCHEMA` | **Data Contract Conformance** | `PASS` | All records conform strictly to FinancialActivityCreate contract schema |
| `SCHEMA` | **Enum Value Constraints** | `PASS` | All direction, activity_type, and provenance values match valid enums |
| `SCHEMA` | **Transaction UUID Constraint** | `PASS` | All transaction IDs conform to valid UUID string standard |
| `INTEGRITY` | **Transaction ID Uniqueness** | `PASS` | 100% of transaction IDs are unique |
| `INTEGRITY` | **Duplicate Record Detection** | `PASS` | Zero duplicate transaction attribute records detected |
| `INTEGRITY` | **Monetary Amount Invariant** | `PASS` | 100% of transaction amounts are strictly positive monetary values |
| `INTEGRITY` | **Direction-Activity Semantics** | `PASS` | All activity types conform to expected natural transaction direction semantics |
| `FINANCIAL` | **Balance Progression Reconstruction** | `PASS` | 100% of recorded balance_after values match exact reconstructed mathematical running balances |
| `FINANCIAL` | **Non-Negative Balance Invariant** | `PASS` | Zero negative account balances detected across all user transaction histories |
| `FINANCIAL` | **Low Liquidity Buffer Alerts** | `WARNING` | Identified user instances with available balance dropping under ৳1,000.00 |
| `TEMPORAL` | **Per-User Chronological Sequence** | `PASS` | All user transaction records maintain strict chronological ordering |
| `TEMPORAL` | **UTC Timezone Invariant** | `PASS` | 100% of timestamps are explicit UTC ISO-8601 representations |

---

## 3. Dataset Overview Statistics

- **Total Users**: 500
- **Total Transactions**: 98884
- **Date Range**: `2026-01-01T08:00:09+00:00` to `2026-12-31T10:50:18+00:00` (365 days)
- **Transactions per User**: Mean = `197.77`, Median = `218.0`, Min = `70`, Max = `283`
- **Inflows**: `7129` transactions | Total = `৳652,728,471.44` | Mean = `৳91,559.61`
- **Outflows**: `91755` transactions | Total = `৳362,375,173.78` | Mean = `৳3,949.38`
- **Amount Distribution**: Mean = `৳10,265.60`, Median = `৳1,711.22`, IQR = `৳2,622.50` (Q25: `৳877.50`, Q75: `৳3,500.00`)
- **Post-Transaction Balance Distribution**: Median = `৳307,208.06`, Min = `৳0.00`, Max = `৳2,416,827.00`

### Transaction Type Distribution

| Activity Type | Count | % Count | Total Volume (৳) |
| :--- | :--- | :--- | :--- |
| `CASH_IN` | 782 | 0.79% | ৳42,274,086.63 |
| `MERCHANT_PAYMENT` | 72423 | 73.24% | ৳121,640,500.22 |
| `MOBILE_RECHARGE` | 2153 | 2.18% | ৳1,335,972.57 |
| `OTHER` | 1764 | 1.78% | ৳54,123,535.99 |
| `P2P_TRANSFER` | 3721 | 3.76% | ৳65,921,584.24 |
| `SALARY` | 4832 | 4.89% | ৳527,950,594.28 |
| `UTILITY_BILL` | 13209 | 13.36% | ৳201,857,371.29 |

---

## 4. Persona Sanity Check Results

Behavioral stats grouped by synthetic user persona (from ground truth metadata):

| Persona Type | User Count | Total Txns | Avg Txns/User | Avg Inflow/User (৳) | Avg Outflow/User (৳) | Net Cash Flow/User (৳) | Min Balance (৳) | Balance Volatility (Std) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `COMMITMENT_HEAVY` | 82 | 18276 | 222.9 | ৳1,854,381.55 | ৳982,279.51 | ৳872,102.05 | ৳0.00 | ৳255,449.31 |
| `FINANCIAL_PRESSURE` | 67 | 6799 | 101.5 | ৳1,077,518.60 | ৳806,948.45 | ৳270,570.15 | ৳0.00 | ৳93,529.24 |
| `IRREGULAR_INCOME` | 93 | 15933 | 171.3 | ৳1,341,697.60 | ৳574,767.27 | ৳766,930.33 | ৳0.00 | ৳233,998.17 |
| `SPENDING_DRIFT` | 73 | 16909 | 231.6 | ৳1,393,633.35 | ৳823,331.44 | ৳570,301.91 | ৳5,644.80 | ৳167,761.80 |
| `STABLE` | 97 | 21729 | 224.0 | ৳1,611,649.02 | ৳782,786.07 | ৳828,862.95 | ৳12,298.36 | ৳242,415.00 |
| `TIGHT_LIQUIDITY` | 88 | 19238 | 218.6 | ৳518,549.68 | ৳434,953.50 | ৳83,596.18 | ৳0.00 | ৳25,095.41 |

---

## 5. Recurring-Pattern Sanity Checks

- **Planted Ground Truth Rules**: `2208` recurring commitments intentionally planted by generator.
- **Observable Repeated Streams Detected**: `4581` recurring candidates identified from transaction history.
- **Planted Rule Observable Detection Rate**: `99.9%`

### Sample Observable Repeated Streams (Top 5)

| Account ID | Counterparty Name | Category | Occurrences | Mean Interval (Days) | Mean Amount (৳) | Amount Std (৳) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ACC-0001` | **Chillox Burgers** | `DINING` | 40 | 9.2 days | ৳759.33 | ৳278.87 |
| `ACC-0001` | **City Bank EMI** | `DEBT_PAYMENT` | 12 | 30.4 days | ৳8,679.00 | ৳0.00 |
| `ACC-0001` | **Dotlines Fiber Internet** | `UTILITIES` | 12 | 30.4 days | ৳2,916.00 | ৳0.00 |
| `ACC-0001` | **Enterprise Payroll Services** | `INCOME` | 12 | 30.4 days | ৳61,508.20 | ৳0.00 |
| `ACC-0001` | **Fitness Plus Gym Membership** | `FITNESS` | 12 | 30.4 days | ৳3,500.00 | ৳0.00 |

---

## 6. Generated Visualizations

### 01 Transaction Amount Distribution
![01_transaction_amount_distribution.png](file:///D:/Programs and Codes/Spendable/reports/plots/01_transaction_amount_distribution.png)

### 02 Monthly Inflow Vs Outflow
![02_monthly_inflow_vs_outflow.png](file:///D:/Programs and Codes/Spendable/reports/plots/02_monthly_inflow_vs_outflow.png)

### 03 User Balance Trajectories
![03_user_balance_trajectories.png](file:///D:/Programs and Codes/Spendable/reports/plots/03_user_balance_trajectories.png)

### 04 Activity Type Distribution
![04_activity_type_distribution.png](file:///D:/Programs and Codes/Spendable/reports/plots/04_activity_type_distribution.png)

### 05 Category Distribution
![05_category_distribution.png](file:///D:/Programs and Codes/Spendable/reports/plots/05_category_distribution.png)

### 06 Persona Comparison
![06_persona_comparison.png](file:///D:/Programs and Codes/Spendable/reports/plots/06_persona_comparison.png)

### 07 User Activity Counts
![07_user_activity_counts.png](file:///D:/Programs and Codes/Spendable/reports/plots/07_user_activity_counts.png)

---

## 7. Findings & Quality Conclusion

1. **Contract Conformance**: The synthetic dataset adheres strictly to the data contract. No extra or leaked ground-truth fields exist in raw feeds.
2. **Mathematical Invariants**: Balance progression reconstruction confirmed 100% precision with zero impossible balance transitions.
3. **Persona Differentiation**: Statistical profiles across `STABLE`, `TIGHT_LIQUIDITY`, `IRREGULAR_INCOME`, `COMMITMENT_HEAVY`, `SPENDING_DRIFT`, and `FINANCIAL_PRESSURE` show clear, meaningful behavioral variations in cash flow, buffer levels, and volatility.
4. **Planted Pattern Quality**: Planted recurring commitments exhibit believable temporal spacing (~30 days for monthly bills) and plausible amount stability.

### Generator Modifications Needed?
**None**. The synthetic generator produces valid, internally consistent, and realistic financial data ready for downstream modeling.

### Dataset Readiness
**READY FOR NEXT STAGE (DATA QUALITY / FEATURE ENGINEERING)**.