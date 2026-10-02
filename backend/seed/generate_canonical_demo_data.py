"""Canonical Static Demo Data Builder for Spendable.

Generates 1 full year (~365 days) of deterministic, chronologically valid transaction histories
for the 5 permanent hackathon demo accounts: Supan, Meraj, Sohana, Noman, and Refat.
"""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path


def create_canonical_demo_data():
    seed_dir = Path("backend/seed")
    if not seed_dir.exists():
        seed_dir = Path("seed")
    seed_dir.mkdir(parents=True, exist_ok=True)

    tx_dir = seed_dir / "demo_transactions"
    tx_dir.mkdir(parents=True, exist_ok=True)

    demo_accounts = [
        {
            "account_id": "acc_supan",
            "username": "supan",
            "display_name": "Supan Roy",
            "currency": "BDT",
            "initial_balance": 45000.0,
            "is_demo_account": True,
            "persona_notes": "Stable regular income, balanced spending, healthy liquidity.",
        },
        {
            "account_id": "acc_meraj",
            "username": "meraj",
            "display_name": "Meraj Hossain",
            "currency": "BDT",
            "initial_balance": 15000.0,
            "is_demo_account": True,
            "persona_notes": "Tight liquidity, high fixed commitments relative to income.",
        },
        {
            "account_id": "acc_sohana",
            "username": "sohana",
            "display_name": "Sohana Rahman",
            "currency": "BDT",
            "initial_balance": 50000.0,
            "is_demo_account": True,
            "persona_notes": "Spending drift with accelerating discretionary shopping over time.",
        },
        {
            "account_id": "acc_noman",
            "username": "noman",
            "display_name": "Noman Ahmed",
            "currency": "BDT",
            "initial_balance": 30000.0,
            "is_demo_account": True,
            "persona_notes": "Irregular freelance income with variable timing and amounts.",
        },
        {
            "account_id": "acc_refat",
            "username": "refat",
            "display_name": "Refat Chowdhury",
            "currency": "BDT",
            "initial_balance": 60000.0,
            "is_demo_account": True,
            "persona_notes": "Commitment heavy with high fixed monthly obligations (Rent, Tuition, EMI).",
        },
    ]

    with open(seed_dir / "demo_accounts.json", mode="w", encoding="utf-8") as f:
        json.dump(demo_accounts, f, indent=2)

    # Base date range: March 1, 2025 to March 1, 2026
    start_date = datetime(2025, 3, 1, 9, 0, 0, tzinfo=timezone.utc)

    # 1. SUPAN: Stable regular salary (65k), rent (18k), utilities (3.5k), internet/netflix (1.5k), groceries & dining
    supan_txs = []
    bal = 45000.0
    ref_seq = 1000

    for month in range(12):
        # Month offset
        m_date = start_date + timedelta(days=month * 30.4)

        # 1st of month: Salary INFLOW 65,000
        ref_seq += 1
        bal += 65000.0
        t1 = m_date.replace(day=1, hour=10, minute=0)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 65000.0,
            "currency": "BDT",
            "direction": "INFLOW",
            "activity_type": "SALARY",
            "timestamp_utc": t1.isoformat(),
            "category": "SALARY",
            "channel": "BANK_TRANSFER",
            "counterparty_name": "Tech Corp BD Ltd",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 3rd of month: Rent OUTFLOW 18,000
        ref_seq += 1
        bal -= 18000.0
        t2 = m_date.replace(day=3, hour=14, minute=30)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 18000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "P2P_TRANSFER",
            "timestamp_utc": t2.isoformat(),
            "category": "HOUSING",
            "channel": "ONLINE_BANKING",
            "counterparty_name": "Gulshan Property Management",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 8th of month: Utilities (DESCO / WASA) 3,500
        ref_seq += 1
        bal -= 3500.0
        t3 = m_date.replace(day=8, hour=11, minute=15)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 3500.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "UTILITY_BILL",
            "timestamp_utc": t3.isoformat(),
            "category": "UTILITIES",
            "channel": "MFS_BKASH",
            "counterparty_name": "DESCO Electric Bill",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 12th of month: Internet & Subscriptions 1,500
        ref_seq += 1
        bal -= 1500.0
        t4 = m_date.replace(day=12, hour=16, minute=0)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 1500.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t4.isoformat(),
            "category": "TELECOM",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "AmberIT Broadband",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Bi-weekly Groceries (7,500 x 2 = 15,000)
        ref_seq += 1
        bal -= 7500.0
        t5 = m_date.replace(day=14, hour=19, minute=20)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 7500.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t5.isoformat(),
            "category": "FOOD_AND_GROCERIES",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "Shwapno Superstore",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        ref_seq += 1
        bal -= 7500.0
        t6 = m_date.replace(day=26, hour=18, minute=45)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 7500.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t6.isoformat(),
            "category": "FOOD_AND_GROCERIES",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "Unimart Gulshan",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Dining / Discretionary (4,000)
        ref_seq += 1
        bal -= 4000.0
        t7 = m_date.replace(day=20, hour=21, minute=10)
        supan_txs.append({
            "reference_id": f"ref_supan_{ref_seq}",
            "account_id": "acc_supan",
            "amount": 4000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t7.isoformat(),
            "category": "DINING",
            "channel": "MFS_NAGAD",
            "counterparty_name": "Takeout Burgers & Cafe",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

    with open(tx_dir / "supan.json", mode="w", encoding="utf-8") as f:
        json.dump(supan_txs, f, indent=2)

    # 2. MERAJ: Tight liquidity (Salary 40k, Rent 16k, Family Transfer 10k, EMI 6k, Utilities 3k -> Total Outflow 35k+)
    meraj_txs = []
    bal = 15000.0
    ref_seq = 2000

    for month in range(12):
        m_date = start_date + timedelta(days=month * 30.4)

        # 1st of month: Salary INFLOW 40,000
        ref_seq += 1
        bal += 40000.0
        t1 = m_date.replace(day=1, hour=9, minute=30)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 40000.0,
            "currency": "BDT",
            "direction": "INFLOW",
            "activity_type": "SALARY",
            "timestamp_utc": t1.isoformat(),
            "category": "SALARY",
            "channel": "BANK_TRANSFER",
            "counterparty_name": "Apex Logistics Ltd",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 2nd of month: Rent 16,000
        ref_seq += 1
        bal -= 16000.0
        t2 = m_date.replace(day=2, hour=11, minute=0)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 16000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "P2P_TRANSFER",
            "timestamp_utc": t2.isoformat(),
            "category": "HOUSING",
            "channel": "MFS_BKASH",
            "counterparty_name": "House Rent Landlord",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 4th of month: Family Remittance 10,000
        ref_seq += 1
        bal -= 10000.0
        t3 = m_date.replace(day=4, hour=15, minute=20)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 10000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "CASH_OUT",
            "timestamp_utc": t3.isoformat(),
            "category": "TRANSFER",
            "channel": "MFS_UPAY",
            "counterparty_name": "Family Support Transfer",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 7th of month: Loan EMI 6,000
        ref_seq += 1
        bal -= 6000.0
        t4 = m_date.replace(day=7, hour=10, minute=0)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 6000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t4.isoformat(),
            "category": "EDUCATION",
            "channel": "ONLINE_BANKING",
            "counterparty_name": "BRAC Bank Micro-Loan EMI",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 10th of month: Utilities 3,000
        ref_seq += 1
        bal -= 3000.0
        t5 = m_date.replace(day=10, hour=14, minute=0)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 3000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "UTILITY_BILL",
            "timestamp_utc": t5.isoformat(),
            "category": "UTILITIES",
            "channel": "MFS_BKASH",
            "counterparty_name": "Titas Gas & Electricity",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Groceries 4,000
        ref_seq += 1
        bal -= 4000.0
        t6 = m_date.replace(day=18, hour=18, minute=0)
        meraj_txs.append({
            "reference_id": f"ref_meraj_{ref_seq}",
            "account_id": "acc_meraj",
            "amount": 4000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t6.isoformat(),
            "category": "FOOD_AND_GROCERIES",
            "channel": "MFS_NAGAD",
            "counterparty_name": "Local Bazaar Grocery",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

    with open(tx_dir / "meraj.json", mode="w", encoding="utf-8") as f:
        json.dump(meraj_txs, f, indent=2)

    # 3. SOHANA: Spending Drift (Salary 75k. Months 0-5: modest 25k spend; Months 6-11: heavy shopping 55k+ spend)
    sohana_txs = []
    bal = 50000.0
    ref_seq = 3000

    for month in range(12):
        m_date = start_date + timedelta(days=month * 30.4)

        # 1st of month: Salary INFLOW 75,000
        ref_seq += 1
        bal += 75000.0
        t1 = m_date.replace(day=1, hour=10, minute=0)
        sohana_txs.append({
            "reference_id": f"ref_sohana_{ref_seq}",
            "account_id": "acc_sohana",
            "amount": 75000.0,
            "currency": "BDT",
            "direction": "INFLOW",
            "activity_type": "SALARY",
            "timestamp_utc": t1.isoformat(),
            "category": "SALARY",
            "channel": "BANK_TRANSFER",
            "counterparty_name": "Creative Media BD",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Fixed Rent 20,000
        ref_seq += 1
        bal -= 20000.0
        t2 = m_date.replace(day=4, hour=12, minute=0)
        sohana_txs.append({
            "reference_id": f"ref_sohana_{ref_seq}",
            "account_id": "acc_sohana",
            "amount": 20000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "BANK_TRANSFER",
            "timestamp_utc": t2.isoformat(),
            "category": "HOUSING",
            "channel": "ONLINE_BANKING",
            "counterparty_name": "Dhanmondi Residency",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Early months (0 to 5): normal shopping 10k. Later months (6 to 11): escalating shopping (35k to 55k)
        disc_amt = 10000.0 if month < 6 else 10000.0 + (month - 5) * 8000.0

        ref_seq += 1
        bal -= disc_amt
        t3 = m_date.replace(day=15, hour=17, minute=30)
        sohana_txs.append({
            "reference_id": f"ref_sohana_{ref_seq}",
            "account_id": "acc_sohana",
            "amount": disc_amt,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t3.isoformat(),
            "category": "DISCRETIONARY_SHOPPING",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "Aarong & Yellow Outlets",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Dining & Cafe (increasing over time)
        dining_amt = 4000.0 if month < 6 else 8000.0 + (month - 5) * 2000.0
        ref_seq += 1
        bal -= dining_amt
        t4 = m_date.replace(day=22, hour=20, minute=15)
        sohana_txs.append({
            "reference_id": f"ref_sohana_{ref_seq}",
            "account_id": "acc_sohana",
            "amount": dining_amt,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t4.isoformat(),
            "category": "DINING",
            "channel": "MFS_BKASH",
            "counterparty_name": "Chef's Table & Gourmet Cafes",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

    with open(tx_dir / "sohana.json", mode="w", encoding="utf-8") as f:
        json.dump(sohana_txs, f, indent=2)

    # 4. NOMAN: Irregular Freelance Income (Inflows: M0 50k, M1 0, M2 90k, M3 30k, M4 0, M5 120k, M6 0, M7 80k, M8 40k, M9 0, M10 110k, M11 35k)
    noman_txs = []
    bal = 30000.0
    ref_seq = 4000

    inflow_schedule = [50000.0, 0.0, 90000.0, 30000.0, 0.0, 120000.0, 0.0, 80000.0, 40000.0, 0.0, 110000.0, 35000.0]

    for month in range(12):
        m_date = start_date + timedelta(days=month * 30.4)

        inf = inflow_schedule[month]
        if inf > 0:
            ref_seq += 1
            bal += inf
            t1 = m_date.replace(day=12, hour=14, minute=0)
            noman_txs.append({
                "reference_id": f"ref_noman_{ref_seq}",
                "account_id": "acc_noman",
                "amount": inf,
                "currency": "BDT",
                "direction": "INFLOW",
                "activity_type": "FREELANCE_INCOME",
                "timestamp_utc": t1.isoformat(),
                "category": "FREELANCE_INCOME",
                "channel": "BANK_TRANSFER",
                "counterparty_name": "Upwork / Global Client Wire",
                "balance_after": round(bal, 2),
                "provenance": "SYNTHETIC",
            })

        # Regular monthly living expenses (22,000)
        ref_seq += 1
        bal -= 15000.0
        t2 = m_date.replace(day=5, hour=11, minute=0)
        noman_txs.append({
            "reference_id": f"ref_noman_{ref_seq}",
            "account_id": "acc_noman",
            "amount": 15000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "BANK_TRANSFER",
            "timestamp_utc": t2.isoformat(),
            "category": "HOUSING",
            "channel": "MFS_BKASH",
            "counterparty_name": "Studio Apartment Rent",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        ref_seq += 1
        bal -= 7000.0
        t3 = m_date.replace(day=18, hour=16, minute=30)
        noman_txs.append({
            "reference_id": f"ref_noman_{ref_seq}",
            "account_id": "acc_noman",
            "amount": 7000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t3.isoformat(),
            "category": "FOOD_AND_GROCERIES",
            "channel": "MFS_NAGAD",
            "counterparty_name": "Local Grocery & Supermarket",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

    with open(tx_dir / "noman.json", mode="w", encoding="utf-8") as f:
        json.dump(noman_txs, f, indent=2)

    # 5. REFAT: Heavy Commitments (Salary 85k; Rent 28k, Tuition 12k, EMI 14k, Utilities 6k, Insurance 4k -> Fixed 64k/mo = 75%)
    refat_txs = []
    bal = 60000.0
    ref_seq = 5000

    for month in range(12):
        m_date = start_date + timedelta(days=month * 30.4)

        # 1st of month: Salary INFLOW 85,000
        ref_seq += 1
        bal += 85000.0
        t1 = m_date.replace(day=1, hour=9, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 85000.0,
            "currency": "BDT",
            "direction": "INFLOW",
            "activity_type": "SALARY",
            "timestamp_utc": t1.isoformat(),
            "category": "SALARY",
            "channel": "BANK_TRANSFER",
            "counterparty_name": "Multinational FMCG Ltd",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 2nd of month: Rent 28,000
        ref_seq += 1
        bal -= 28000.0
        t2 = m_date.replace(day=2, hour=11, minute=30)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 28000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "BANK_TRANSFER",
            "timestamp_utc": t2.isoformat(),
            "category": "HOUSING",
            "channel": "ONLINE_BANKING",
            "counterparty_name": "Uttara Flat Landlord",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 5th of month: Car Loan EMI 14,000
        ref_seq += 1
        bal -= 14000.0
        t3 = m_date.replace(day=5, hour=10, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 14000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t3.isoformat(),
            "category": "TRANSPORT",
            "channel": "ONLINE_BANKING",
            "counterparty_name": "Eastern Bank Auto Loan EMI",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 8th of month: Child Education Tuition 12,000
        ref_seq += 1
        bal -= 12000.0
        t4 = m_date.replace(day=8, hour=14, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 12000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t4.isoformat(),
            "category": "EDUCATION",
            "channel": "MFS_BKASH",
            "counterparty_name": "Scholastica School Fee",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 12th of month: Utilities & Maintenance 6,000
        ref_seq += 1
        bal -= 6000.0
        t5 = m_date.replace(day=12, hour=15, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 6000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "UTILITY_BILL",
            "timestamp_utc": t5.isoformat(),
            "category": "UTILITIES",
            "channel": "MFS_NAGAD",
            "counterparty_name": "WASA & Building Society Maintenance",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # 15th of month: Health / Life Insurance 4,000
        ref_seq += 1
        bal -= 4000.0
        t6 = m_date.replace(day=15, hour=16, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 4000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t6.isoformat(),
            "category": "HEALTH",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "MetLife Insurance Premium",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

        # Groceries & Living 10,000
        ref_seq += 1
        bal -= 10000.0
        t7 = m_date.replace(day=22, hour=19, minute=0)
        refat_txs.append({
            "reference_id": f"ref_refat_{ref_seq}",
            "account_id": "acc_refat",
            "amount": 10000.0,
            "currency": "BDT",
            "direction": "OUTFLOW",
            "activity_type": "MERCHANT_PAYMENT",
            "timestamp_utc": t7.isoformat(),
            "category": "FOOD_AND_GROCERIES",
            "channel": "CARD_PAYMENT",
            "counterparty_name": "Agora Superstore",
            "balance_after": round(bal, 2),
            "provenance": "SYNTHETIC",
        })

    with open(tx_dir / "refat.json", mode="w", encoding="utf-8") as f:
        json.dump(refat_txs, f, indent=2)

    print("[Canonical Generator] Built demo accounts and 5 transaction files successfully.")


if __name__ == "__main__":
    create_canonical_demo_data()
