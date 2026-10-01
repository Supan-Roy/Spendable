# Spendable — Financial Data Contract & Domain Foundation

## 1. Overview & Purpose
This document defines the foundational financial data contract for **Spendable**. Spendable is an AI-powered personal financial runway and liquidity intelligence product built to answer the customer question: *"Know what you can safely spend."*

Before building analytical forecasting models, machine learning, or natural language explanations, Spendable requires a strict, explicit, and sound domain contract for observed financial activity.

---

## 2. Core Architectural Principle: Data Classification

Spendable strictly delineates data into three explicit tiers:

```
[ OBSERVED ]  ───>  [ INFERRED ]  ───>  [ PREDICTED ]
Raw, verified      Behavioral          Runway forecasts
financial events   patterns & trends   & pressure estimates
```

1. **OBSERVED (Raw Financial Activity)**:
   - Ground truth events that actually occurred at an exact timestamp.
   - Example: A merchant payment of `৳2,500.00` occurred on `2026-09-05T09:30:00Z`.
   - *Status: Defined and implemented in this foundation layer.*

2. **INFERRED (Derived Behavioral Intelligence)**:
   - Analytical patterns recognized over observed events.
   - Example: A payment of ~`৳2,500.00` recurs every ~30 days around the 5th of the month.
   - *Status: Intentionally separated. To be built in future intelligence layers.*

3. **PREDICTED (Future Liquidity & Runway Trajectory)**:
   - Estimates of future financial position, expected inflows/outflows, and liquidity pressure.
   - Example: `৳7,850.00` estimated safe spendable capacity for the next 14 days.
   - *Status: Intentionally separated. To be built in future prediction layers.*

---

## 3. Data Honesty Principles & Scope Boundaries

Spendable explicitly acknowledges the boundaries of observable data:
- **No Unobservable Facts**: Spendable only observes activity recorded in the connected wallet/account feed.
- **Cash Out Handling**: A cash withdrawal is recorded as an observed `CASH_OUT` outflow event. The subsequent physical cash usage is **unobservable** and is never modeled as a known fact.
- **External Account Independence**: Undocumented income, external bank accounts, or physical cash balances are treated as unavailable unless explicitly imported.
- **Nullable Optional Context**: Merchant names, categories, reference IDs, and post-transaction balances are optional fields. The domain model functions completely when context is missing.

---

## 4. Domain Data Representation Standards

### A. Monetary Representation
- **Data Type**: `Decimal` in Python (via `pydantic.condecimal`) and `NUMERIC(14, 2)` in PostgreSQL.
- **No Floating-Point**: Floating-point numbers (`float`) are strictly forbidden for financial arithmetic to prevent rounding anomalies.
- **Amount Semantics**: `amount` is always a strictly positive value (`Decimal > 0.00`). Transaction direction (`INFLOW` vs `OUTFLOW`) dictates the flow of funds.
- **Currency**: Represented explicitly as an ISO-4217 3-letter currency code (default: `"BDT"`).

### B. Temporal Representation
- **Timestamp Standard**: Timestamps are strictly timezone-aware UTC ISO-8601 representations (`DateTime(timezone=True)` in PostgreSQL).
- **Format**: `YYYY-MM-DDTHH:MM:SSZ` (e.g. `2026-10-02T14:30:00Z`).
- **Ordering**: Transactions maintain chronological ordering based on `timestamp_utc`.

### C. Transaction Direction & Activity Semantics
- **Direction (`TransactionDirection`)**:
  - `INFLOW`: Funds entering the account (increases balance).
  - `OUTFLOW`: Funds leaving the account (decreases balance).
- **Activity Types (`ActivityType`)**:
  - `MERCHANT_PAYMENT`: Outflow purchase at a merchant/store.
  - `UTILITY_BILL`: Outflow utility/bill payment (electricity, water, internet).
  - `MOBILE_RECHARGE`: Outflow mobile airtime recharge.
  - `P2P_TRANSFER`: Inflow or outflow peer-to-peer transfer.
  - `CASH_OUT`: Outflow cash withdrawal via agent or ATM.
  - `CASH_IN`: Inflow cash deposit via agent or bank.
  - `SALARY`: Inflow salary/payroll deposit.
  - `FEE`: Outflow service or transaction fee.
  - `OTHER`: General/unclassified financial event.

---

## 5. Schema Definition & Field Rules

### `FinancialActivity` (Observed Event Entity)

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Yes | Unique primary identifier (v4 UUID). |
| `account_id` | `String(64)` | Yes | Identifier of the account/wallet. |
| `amount` | `Decimal(14, 2)` | Yes | Strictly positive monetary amount (`> 0.00`). |
| `currency` | `String(3)` | Yes | ISO-4217 currency code (default `"BDT"`). |
| `direction` | `TransactionDirection` | Yes | `INFLOW` or `OUTFLOW`. |
| `activity_type` | `ActivityType` | Yes | Categorical event classification. |
| `timestamp_utc` | `DateTime(UTC)` | Yes | Precise UTC execution time. |
| `category` | `String(64)` | No | Optional domain category (e.g. `"UTILITIES"`). |
| `channel` | `String(32)` | No | Optional channel (e.g. `"APP"`, `"AGENT"`, `"ATM"`). |
| `counterparty_name` | `String(128)` | No | Optional merchant/sender/payee name. |
| `reference_id` | `String(128)` | No | External transaction reference number. |
| `balance_after` | `Decimal(14, 2)` | No | Directly observed post-transaction balance. |
| `provenance` | `DataProvenance` | Yes | Source of record: `SYNTHETIC`, `IMPORTED`, or `USER_PROVIDED`. |
| `created_at` | `DateTime(UTC)` | Yes | System ingestion timestamp. |

---

## 6. Validation Rules & Invariants

1. **Amount Invariant**: `amount > 0.00`. Negative amounts are rejected at validation.
2. **Balance Invariant**: If `balance_after` is provided, `balance_after >= 0.00`.
3. **Currency Invariant**: `currency` must be a valid 3-letter uppercase string (e.g. `"BDT"`).
4. **Time Invariant**: `timestamp_utc` must specify an explicit UTC timezone.
5. **Direction Consistency**: Ingestion validation ensures `CASH_IN` and `SALARY` default to `INFLOW`, while `CASH_OUT`, `MERCHANT_PAYMENT`, `UTILITY_BILL`, and `FEE` default to `OUTFLOW`.

---

## 7. Future Intelligence Extension Points

This data contract is designed to cleanly feed future downstream modules without requiring schema redesign:
- **Synthetic Generator Layer**: Can generate realistic temporal transaction feeds conforming to this contract.
- **Feature Layer**: Can compute rolling 7/14/30-day inflow/outflow metrics directly from `timestamp_utc`, `amount`, and `direction`.
- **Forecasting & Spendable Engine**: Will consume observed activities to project liquidity pressure and calculate safe spendable runway.
