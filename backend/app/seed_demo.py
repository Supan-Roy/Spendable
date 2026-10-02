"""Idempotent Demo Account & Transaction Seeding Script.

Seeds the 5 permanent repository-backed demo accounts (Supan, Meraj, Sohana, Noman, Refat)
and their 1-year historical transaction files from Git storage into application tables.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Any

from app.database import engine, SessionLocal, Base
from app.models.account import UserAccount
from app.models.activity import FinancialActivityModel
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.auth import hash_password


def seed_demo_accounts(session_factory=None) -> Dict[str, Any]:
    """Seed permanent demo accounts and transaction histories into database.
    
    Guarantees strict idempotency (safe to execute multiple times or during Railway startup).
    """
    from app.database import engine as default_engine, SessionLocal as default_session_factory
    
    s_factory = session_factory or default_session_factory
    bind_engine = getattr(s_factory, "kw", {}).get("bind") or default_engine
    
    Base.metadata.create_all(bind=bind_engine)

    # Locate canonical seed directory
    seed_dir = Path("backend/seed")
    if not seed_dir.exists() and Path("seed").exists():
        seed_dir = Path("seed")
    elif not seed_dir.exists() and Path("../seed").exists():
        seed_dir = Path("../seed")

    accounts_json = seed_dir / "demo_accounts.json"
    tx_dir = seed_dir / "demo_transactions"

    if not accounts_json.exists():
        print(f"[SeedDemo] Warning: demo_accounts.json not found at {accounts_json}")
        return {"status": "failed", "error": "demo_accounts.json not found"}

    with open(accounts_json, mode="r", encoding="utf-8") as f:
        demo_accounts = json.load(f)

    session = s_factory()
    accounts_created = 0
    activities_inserted = 0

    try:
        # Default demo password for all 5 demo accounts
        default_pwd_hash = hash_password("password123")

        for acc_meta in demo_accounts:
            acc_id = acc_meta["account_id"]
            uname = acc_meta["username"]
            display_name = acc_meta["display_name"]
            curr = acc_meta.get("currency", "BDT")
            init_bal = acc_meta.get("initial_balance", 0.0)

            # 1. Create or retrieve UserAccount record
            user = session.query(UserAccount).filter(UserAccount.account_id == acc_id).first()
            if not user:
                user = UserAccount(
                    account_id=acc_id,
                    username=uname,
                    password_hash=default_pwd_hash,
                    display_name=display_name,
                    currency=curr,
                    current_balance=init_bal,
                    is_demo_account=True,
                )
                session.add(user)
                accounts_created += 1
            else:
                user.is_demo_account = True
                if not user.username:
                    user.username = uname

            # 2. Load and insert canonical transaction history
            tx_file = tx_dir / f"{uname}.json"
            if tx_file.exists():
                with open(tx_file, mode="r", encoding="utf-8") as tf:
                    txs = json.load(tf)

                existing_refs = set(
                    r[0] for r in session.query(FinancialActivityModel.reference_id)
                    .filter(FinancialActivityModel.account_id == acc_id)
                    .all()
                    if r[0] is not None
                )

                last_balance = float(user.current_balance)

                for item in txs:
                    ref_id = item["reference_id"]
                    if ref_id in existing_refs:
                        continue  # Skip duplicate

                    ts_utc = datetime.fromisoformat(item["timestamp_utc"])
                    if ts_utc.tzinfo is None:
                        ts_utc = ts_utc.replace(tzinfo=timezone.utc)

                    direction_enum = TransactionDirection(item["direction"].upper())
                    try:
                        activity_type_enum = ActivityType(item["activity_type"].upper())
                    except Exception:
                        activity_type_enum = ActivityType.P2P_TRANSFER

                    bal_after = float(item["balance_after"])
                    last_balance = bal_after

                    act_obj = FinancialActivityModel(
                        account_id=acc_id,
                        amount=float(item["amount"]),
                        currency=str(item.get("currency", "BDT")),
                        direction=direction_enum,
                        activity_type=activity_type_enum,
                        timestamp_utc=ts_utc,
                        category=item.get("category"),
                        channel=item.get("channel"),
                        counterparty_name=item.get("counterparty_name"),
                        reference_id=ref_id,
                        balance_after=bal_after,
                        provenance=DataProvenance.SYNTHETIC,
                    )
                    session.add(act_obj)
                    existing_refs.add(ref_id)
                    activities_inserted += 1

                user.current_balance = last_balance

        session.commit()
        print(f"[SeedDemo] Completed: {accounts_created} accounts created/updated, {activities_inserted} activities inserted.")
        return {
            "status": "success",
            "accounts_created": accounts_created,
            "activities_inserted": activities_inserted,
        }
    except Exception as e:
        session.rollback()
        print(f"[SeedDemo] Failed: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        session.close()


if __name__ == "__main__":
    seed_demo_accounts()
