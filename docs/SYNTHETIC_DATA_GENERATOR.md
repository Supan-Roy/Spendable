# Spendable — Synthetic Financial Data Generator

## 1. Overview & Goal

Spendable requires believable, reproducible temporal financial transaction feeds to train and evaluate future intelligence modules (recurring payment detection, spending pattern analysis, cash-flow forecasting, Spendable estimation, and scenario simulation) without using real private customer data.

The **Synthetic Financial Data Generator** produces realistic financial activity strictly conforming to the Spendable Financial Data Contract ([docs/FINANCIAL_DATA_CONTRACT.md](file:///d:/Programs%20and%20Codes/Spendable/docs/FINANCIAL_DATA_CONTRACT.md)).

---

## 2. Core Architecture & Pipeline

```
[ Generator Config ] ──> [ Persona Simulation ] ──> [ Temporal Day Engine ]
        │                       │                             │
  (seed, users,          (Behavioral Rules &          (Day-by-Day Stream &
  days, start_date)       Planted Templates)           Balance Progression)
                                                              │
                                            ┌─────────────────┴─────────────────┐
                                            ▼                                   ▼
                                 [ Raw Activity Feed ]               [ Ground Truth Metadata ]
                                 (CSV / JSON / DB Seed)              (Rules, Milestones, Annotations)
```

1. **Configuration**: Defines deterministic random seed, user count, simulation duration, start date, currency, and persona weighting.
2. **Persona Behavioral Profiles**: Instantiates behavioral rules, starting liquidity buffers, income rhythms, recurring commitment templates, and discretionary spending distributions.
3. **Temporal Day Engine**: Simulates day-by-day activity chronologically, assigning timestamps, enforcing monetary decimal precision, and calculating running `balance_after` progress.
4. **Validation Suite**: Automatically validates every record against `FinancialActivityCreate` schema, checking balance progression consistency, timestamp ordering, and ID uniqueness.
5. **Separate Ground Truth**: Maintains internal ground-truth metadata separately from observable customer-facing transactions.

---

## 3. Available Behavioral Personas

| Persona Type | Key Behavioral Characteristics | Primary Temporal Patterns |
| :--- | :--- | :--- |
| `STABLE` | Regular high income, predictable expenses, healthy liquidity buffer. | Monthly salary on 1st-5th, recurring bills (rent, utilities, internet), steady weekend dining/groceries. |
| `TIGHT_LIQUIDITY` | Modest income, heavy fixed commitments (~70-85% of income), small remaining buffer. | Monthly salary, high rent/family transfer obligation, low month-end liquidity buffer. |
| `IRREGULAR_INCOME` | Variable/irregular inflows (freelance, contract), variable discretionary expenses. | Payouts every 10–25 days from varied counterparties, irregular cash-flow curves. |
| `COMMITMENT_HEAVY` | High density of recurring obligations across multiple frequencies. | 7-10 recurring subscriptions/bills (rent, loan EMI, internet, streaming, gym, family transfer). |
| `SPENDING_DRIFT` | Baseline stability during 1st half, followed by gradual discretionary spending drift in 2nd half. | `DRIFT_START` milestone at 50% duration; discretionary frequency increases 1.5x-2.2x. |
| `FINANCIAL_PRESSURE` | Baseline stability initially; medical/emergency commitments surge later, deteriorating liquidity. | `PRESSURE_START` milestone at 33% duration; recurring/emergency outflows strain buffer. |

---

## 4. Ground-Truth Metadata Strategy

Spendable strictly separates **Observable Facts** from **Internal Ground Truth**:

- **Observable Customer Transaction Feed** (`FinancialActivityCreate`): Contains ONLY ground-truth observable transaction attributes (`id`, `account_id`, `amount`, `currency`, `direction`, `activity_type`, `timestamp_utc`, `category`, `channel`, `counterparty_name`, `reference_id`, `balance_after`, `provenance`). No internal labels like `is_recurring` or `persona` exist in raw feeds.
- **Ground Truth Storage** (`DatasetGroundTruth`): Stored separately in `ground_truth.json` or ground-truth data models. Tracks:
  - User starting balances and persona allocations.
  - Planted recurring rule definitions (`rule_id`, target frequency, base amount, target day).
  - Behavioral milestone timelines (`DRIFT_START`, `PRESSURE_START`).
  - Transaction annotations mapping `activity_id` to its planted rule origin and persona phase label.

This separation enables unbiased, objective evaluation of future ML recurring detection algorithms.

---

## 5. Configuration Options

`GeneratorConfig` parameter fields:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `seed` | `int` | `42` | Random seed for 100% deterministic reproducibility. |
| `num_users` | `int` | `10` | Total synthetic user accounts to generate. |
| `start_date` | `datetime` | `2026-01-01T00:00:00Z` | Historical simulation start date (UTC). |
| `duration_days` | `int` | `180` | Historical simulation duration in days. |
| `currency` | `str` | `"BDT"` | ISO-4217 3-letter currency code. |
| `persona_weights` | `Dict[PersonaType, float]` | `None` | Optional custom probability weights across personas. |

---

## 6. CLI Commands & Examples

### Generating a Synthetic Dataset

Generate a 180-day synthetic dataset with 10 users using random seed `42`:

```bash
python -m app.synthetic.cli --seed 42 --users 10 --days 180 --output-dir ./synthetic_output
```

CLI options:
- `--seed`: Integer seed for reproducibility (default: 42).
- `--users`: Number of synthetic users (default: 10).
- `--days`: Duration in days (default: 180).
- `--start-date`: Start date YYYY-MM-DD (default: 2026-01-01).
- `--output-dir`: Destination directory for output files (default: `./synthetic_output`).
- `--seed-db`: Optional flag to seed generated records directly into the connected database.

### Generated Files

The CLI generates three primary files in the output directory:
- `transactions.csv`: Observable raw financial activity feed in CSV format.
- `transactions.json`: Observable raw financial activity feed in JSON format.
- `ground_truth.json`: Ground truth metadata (user personas, planted rules, annotations).

---

## 7. Running Unit & Integration Tests

Run the full pytest suite:

```bash
venv\Scripts\pytest backend/tests
```

Key generator property & invariant tests:
- `test_generator_reproducibility`: Confirms identical seeds yield 100% identical transaction feeds and ground truth annotations.
- `test_data_contract_conformance`: Verifies every record passes `FinancialActivityCreate` validation.
- `test_balance_progression_consistency`: Verifies `balance_after` mathematically matches `Starting Balance + Inflows - Outflows`.
- `test_ground_truth_separation`: Ensures zero ground-truth leak fields appear in observable activity feeds.
- `test_persona_expectations`: Verifies persona behavioral milestones and planted recurring rules.
