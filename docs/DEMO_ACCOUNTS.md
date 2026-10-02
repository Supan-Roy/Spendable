# Spendable Persistent Demo Accounts & Authentication Architecture

This document describes the 5 permanent hackathon demo accounts, their intentionally designed transaction behaviors, repository-backed static data storage, authentication architecture, and deployment seeding pipeline.

---

## 1. The 5 Permanent Seeded Demo Accounts

To allow hackathon judges and users to explore distinct personal financial behaviors without manual data entry or account creation, Spendable provides **five permanent, seeded demo accounts**.

| Account Name | Username | Account ID | Default State | Persona & Financial Behavior Description |
| :--- | :--- | :--- | :--- | :--- |
| **Supan** *(Default)* | `supan` | `acc_supan` | `HEALTHY` | **Baseline Core Experience**: Regular salary (৳65,000/mo), balanced housing rent, utilities, broadband, and bi-weekly groceries. Demonstrates standard healthy Spendable calculations. |
| **Meraj** | `meraj` | `acc_meraj` | `WATCH` / `PRESSURED` | **Tight Liquidity & High Obligations**: Salary ৳40,000/mo with fixed rent (৳16,000), family remittance (৳10,000), loan EMI (৳6,000), and utilities. Low remaining balance and low discretionary room. |
| **Sohana** | `sohana` | `acc_sohana` | Accelerating Volatility | **Spending-Drift & Discretionary Heavy**: Salary ৳75,000/mo. Moderate early spending that accelerates into heavy shopping/dining in later months, driving up spending volatility and drawdown. |
| **Noman** | `noman` | `acc_noman` | Income Volatility | **Irregular Freelance Income**: Inflows arrive at varying dates and amounts (৳35,000 to ৳120,000 with gap months). Adaptive safety reserve adjusts dynamically to income volatility. |
| **Refat** | `refat` | `acc_refat` | High Protected Burden | **Commitment Heavy**: Salary ৳85,000/mo with ~75% fixed monthly commitments (Rent ৳28k, Tuition ৳12k, EMI ৳14k, Utilities ৳6k, Insurance ৳4k). High balance but small safe spendable capacity. |

---

## 2. Default Session & Account Switching UX Flow

```
┌────────────────────────────────────────────────────────┐
│               First Visit (No JWT Session)             │
└───────────────────────────┬────────────────────────────┘
                            │
            Auto-authenticate as Supan
            (Obtains real JWT token)
                            │
                            ▼
                  Spendable Dashboard
                            │
               ┌────────────┴────────────┐
               │  Demo Account Switcher  │
               └────────────┬────────────┘
                            │
         Select Meraj / Sohana / Noman / Refat
                            │
                            ▼
            Obtains new signed JWT token
            Reloads authenticated dashboard
```

1. **First Visit**: If no valid JWT token is stored in the browser, the frontend automatically triggers the demo login endpoint (`POST /api/v1/auth/demo-login/supan`) to obtain a real signed JWT for Supan.
2. **Account Switcher**: Selecting another demo account issues a new JWT token for that account, allowing judges to compare different Spendable calculation outputs immediately.
3. **Logout**: Clears the JWT session and returns the user to the Login screen displaying the 5 Demo Account cards alongside normal username/password registration.

---

## 3. Canonical Repository-Backed Seed Storage

* **No Runtime Random Generation**: Demo accounts and transaction histories are **100% deterministic** and committed directly to Git.
* **Canonical Storage Location**:
  * `backend/seed/demo_accounts.json` (Account profiles & metadata)
  * `backend/seed/demo_transactions/supan.json`
  * `backend/seed/demo_transactions/meraj.json`
  * `backend/seed/demo_transactions/sohana.json`
  * `backend/seed/demo_transactions/noman.json`
  * `backend/seed/demo_transactions/refat.json`
* **Historical Range**: Each account contains **~1 full year (365 days)** of chronologically valid, mathematically consistent transaction history.

---

## 4. Demo Account Immutability & Security

* **`is_demo_account = true`**: Demo accounts are explicitly tagged in the `user_accounts` table.
* **Protection Rules**:
  * Demo accounts cannot be deleted or overwritten by normal registration.
  * Re-running the seed process is **idempotent** and will create **0 duplicate transactions**.
  * User credentials are encrypted using standard **bcrypt** password hashing.

---

## 5. Railway Deployment Automatic Seeding

When deployed to Railway (or any containerized host), the application initialization flow runs automatically during boot:

```bash
# Railway / Server Startup Command Sequence
python -m alembic upgrade head && python -m app.seed_demo && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

* **App Startup Hook**: FastAPI `lifespan` context in [`backend/app/main.py`](file:///d:/Programs%20and%20Codes/Spendable/backend/app/main.py) also invokes `seed_demo_accounts()` on startup, ensuring the 5 demo accounts exist in fresh PostgreSQL databases without manual terminal intervention.

---

## 6. Commands & Verification

### Local Database Seeding
```bash
python -m app.seed_demo
```

### Reset & Reseed Development Database
```bash
# Delete local SQLite DB file and run migrations & seed
rm spendable.db
python -m alembic upgrade head
python -m app.seed_demo
```

### Run Test Suite
```bash
pytest backend/tests/test_demo_and_auth.py
```
