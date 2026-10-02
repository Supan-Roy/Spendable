"""Synthetic Data Seeding Script for Spendable Application Database.

Seeds demo user accounts and financial activities from synthetic datasets into application database tables.
Guarantees strict idempotency (safe to run multiple times without duplicating records).
"""

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.models.account import UserAccount
from app.models.activity import FinancialActivityModel
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance


def seed_database(data_dir: str = "data", limit_accounts: int = 5) -> dict:
    """Seed application database tables with demo user accounts and activities.
    
    Returns a dictionary summary of inserted records.
    """
    # Ensure data directory exists
    session: Session = SessionLocal()
    try:
        data_path = Path(data_dir)
        if not data_path.exists() and Path(f"../{data_dir}").exists():
            data_path = Path(f"../{data_dir}")
        tx_path = data_path / "transactions.csv"
        feat_path = data_path / "features" / "features_test.csv"
        if not feat_path.exists():
            feat_path = data_path / "features_test.csv"

        if not tx_path.exists():
            print(f"[Seed] Error: transactions.csv not found at {tx_path}")
            return {"accounts_created": 0, "activities_created": 0, "status": "failed"}

        tx_df = pd.read_csv(tx_path)

        # Identify unique demo user accounts
        acc_col = "account_id" if "account_id" in tx_df.columns else "user_id"
        unique_accounts = list(tx_df[acc_col].unique())[:limit_accounts]

        # Ensure demo account ACC-DEMO-001 is included if present
        if "ACC-DEMO-001" in tx_df[acc_col].unique() and "ACC-DEMO-001" not in unique_accounts:
            unique_accounts.insert(0, "ACC-DEMO-001")

        accounts_created = 0
        activities_created = 0

        for account_id in unique_accounts:
            acc_txs = tx_df[tx_df[acc_col] == account_id].sort_values(by="timestamp_utc" if "timestamp_utc" in tx_df.columns else "timestamp")

            if len(acc_txs) == 0:
                continue

            latest_tx = acc_txs.iloc[-1]
            last_balance = float(latest_tx.get("balance_after", 0.0)) if pd.notna(latest_tx.get("balance_after")) else 0.0

            # 1. Create or retrieve UserAccount
            existing_user = session.query(UserAccount).filter(UserAccount.account_id == account_id).first()
            if not existing_user:
                display_name = f"Demo Account ({account_id})"
                user_obj = UserAccount(
                    account_id=account_id,
                    display_name=display_name,
                    currency="BDT",
                    current_balance=last_balance,
                )
                session.add(user_obj)
                accounts_created += 1
            else:
                existing_user.current_balance = last_balance

            # 2. Seed FinancialActivityModel records idempotently
            existing_refs = set(
                r[0] for r in session.query(FinancialActivityModel.reference_id)
                .filter(FinancialActivityModel.account_id == account_id)
                .all()
                if r[0] is not None
            )

            for idx, row in acc_txs.iterrows():
                ref_id = str(row.get("reference_id", row.get("transaction_id", f"tx_{account_id}_{idx}")))
                if ref_id in existing_refs:
                    continue  # Skip duplicate

                # Parse timestamp
                raw_ts = str(row.get("timestamp_utc", row.get("timestamp", "")))
                try:
                    ts_utc = datetime.fromisoformat(raw_ts)
                    if ts_utc.tzinfo is None:
                        ts_utc = ts_utc.replace(tzinfo=timezone.utc)
                except Exception:
                    ts_utc = datetime.now(timezone.utc)

                direction_str = str(row.get("direction", "OUTFLOW")).upper()
                try:
                    direction_enum = TransactionDirection(direction_str)
                except Exception:
                    direction_enum = TransactionDirection.OUTFLOW

                act_type_str = str(row.get("activity_type", "MERCHANT_PAYMENT")).upper()
                try:
                    act_type_enum = ActivityType(act_type_str)
                except Exception:
                    act_type_enum = ActivityType.MERCHANT_PAYMENT

                act_obj = FinancialActivityModel(
                    account_id=account_id,
                    amount=float(row.get("amount", 0.0)),
                    currency=str(row.get("currency", "BDT")),
                    direction=direction_enum,
                    activity_type=act_type_enum,
                    timestamp_utc=ts_utc,
                    category=str(row.get("category")) if pd.notna(row.get("category")) else None,
                    channel=str(row.get("channel")) if pd.notna(row.get("channel")) else None,
                    counterparty_name=str(row.get("counterparty_name")) if pd.notna(row.get("counterparty_name")) else None,
                    reference_id=ref_id,
                    balance_after=float(row.get("balance_after")) if pd.notna(row.get("balance_after")) else None,
                    provenance=DataProvenance.SYNTHETIC,
                )
                session.add(act_obj)
                existing_refs.add(ref_id)
                activities_created += 1

        session.commit()
        print(f"[Seed] Completed successfully: {accounts_created} accounts created/updated, {activities_created} activities inserted.")
        return {
            "accounts_created": accounts_created,
            "activities_created": activities_created,
            "status": "success",
        }
    except Exception as e:
        session.rollback()
        print(f"[Seed] Execution failed: {e}")
        return {"accounts_created": 0, "activities_created": 0, "error": str(e), "status": "failed"}
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
