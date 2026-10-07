"""CSV Transaction Ingestion Adapter for Spendable.

Parses, validates, normalizes, deduplicates, and persists user transaction activity from CSV files.
Enforces account ownership and invalidates forecast caches upon completion.
"""

from datetime import datetime, timezone
import io
import pandas as pd
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from app.ingestion.base import BaseIngestionAdapter
from app.ingestion.schema import IngestionResult, CanonicalTransaction
from app.domain.enums import TransactionDirection, ActivityType, DataProvenance
from app.models.activity import FinancialActivityModel
from app.models.account import UserAccount
from app.forecasting.cache import forecast_cache


class CSVTransactionAdapter(BaseIngestionAdapter):
    """Adapter for importing and normalizing CSV transaction files."""

    def __init__(self):
        super().__init__(adapter_name="CSV_IMPORT_ADAPTER")

    def ingest_records(
        self, raw_data: Union[str, bytes, io.BytesIO, List[Dict[str, Any]]], target_account_id: str, db: Session
    ) -> IngestionResult:
        result = IngestionResult(adapter_name=self.adapter_name, account_id=target_account_id)

        # 1. Account ownership check
        account = db.query(UserAccount).filter(UserAccount.account_id == target_account_id).first()
        if not account:
            result.errors.append(f"Target account '{target_account_id}' does not exist in database")
            return result

        # 2. Parse CSV input into DataFrame
        try:
            if isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            elif isinstance(raw_data, bytes):
                df = pd.read_csv(io.BytesIO(raw_data))
            elif isinstance(raw_data, str):
                df = pd.read_csv(io.StringIO(raw_data))
            elif isinstance(raw_data, io.BytesIO):
                df = pd.read_csv(raw_data)
            else:
                result.errors.append(f"Unsupported input data type: {type(raw_data)}")
                return result
        except Exception as e:
            result.errors.append(f"Failed to parse CSV payload: {str(e)}")
            return result

        result.total_records = len(df)
        if len(df) == 0:
            return result

        # Normalize column names (strip whitespace and lower case)
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Map common column aliases
        col_map = {
            "tx_id": "reference_id",
            "ref_id": "reference_id",
            "date": "timestamp_utc",
            "timestamp": "timestamp_utc",
            "datetime": "timestamp_utc",
            "type": "activity_type",
            "counterparty": "counterparty_name",
        }
        df = df.rename(columns=col_map)

        # Fetch existing reference IDs for target account to perform fast deduplication
        existing_refs = set(
            r[0] for r in db.query(FinancialActivityModel.reference_id)
            .filter(FinancialActivityModel.account_id == target_account_id)
            .filter(FinancialActivityModel.reference_id.isnot(None))
            .all()
        )

        canonical_list: List[CanonicalTransaction] = []
        activities_to_insert: List[FinancialActivityModel] = []
        current_bal = float(account.current_balance)

        for idx, row in df.iterrows():
            row_dict = row.to_dict()

            # Required field checks
            raw_amount = row_dict.get("amount")
            raw_direction = str(row_dict.get("direction", "")).strip().upper()
            raw_ts = row_dict.get("timestamp_utc")

            if raw_amount is None or pd.isna(raw_amount):
                result.invalid_records += 1
                result.errors.append(f"Row {idx+1}: Missing required 'amount'")
                continue

            try:
                amt = float(raw_amount)
                if amt <= 0.0:
                    result.invalid_records += 1
                    result.errors.append(f"Row {idx+1}: Amount must be positive (> 0.0)")
                    continue
            except Exception:
                result.invalid_records += 1
                result.errors.append(f"Row {idx+1}: Invalid numerical amount '{raw_amount}'")
                continue

            # Direction validation
            if raw_direction not in ("INFLOW", "OUTFLOW"):
                result.invalid_records += 1
                result.errors.append(f"Row {idx+1}: Direction must be INFLOW or OUTFLOW (got '{raw_direction}')")
                continue

            dir_enum = TransactionDirection.INFLOW if raw_direction == "INFLOW" else TransactionDirection.OUTFLOW

            # Timestamp parsing
            parsed_dt = None
            if raw_ts and not pd.isna(raw_ts):
                try:
                    parsed_dt = pd.to_datetime(raw_ts, utc=True).to_pydatetime()
                except Exception:
                    pass

            if parsed_dt is None:
                parsed_dt = datetime.now(timezone.utc)

            ref_id = str(row_dict.get("reference_id")).strip() if row_dict.get("reference_id") and not pd.isna(row_dict.get("reference_id")) else None

            # Deduplication check
            if ref_id and ref_id in existing_refs:
                result.duplicates_skipped += 1
                continue

            idempotency_hash = self.generate_idempotency_hash(
                account_id=target_account_id,
                reference_id=ref_id,
                amount=amt,
                timestamp_str=parsed_dt.isoformat(),
                direction_str=raw_direction,
            )

            # Update balance_after calculation
            if dir_enum == TransactionDirection.INFLOW:
                current_bal += amt
            else:
                current_bal -= amt

            cat = str(row_dict.get("category", "MISCELLANEOUS")).strip().upper()
            channel = str(row_dict.get("channel", "CSV_IMPORT")).strip().upper()
            counterparty = str(row_dict.get("counterparty_name", "CSV Import Counterparty")).strip()

            act_model = FinancialActivityModel(
                account_id=target_account_id,
                amount=round(amt, 2),
                currency="BDT",
                direction=dir_enum.value,
                activity_type=str(row_dict.get("activity_type", "MERCHANT_PAYMENT")).strip().upper(),
                timestamp_utc=parsed_dt,
                category=cat,
                channel=channel,
                counterparty_name=counterparty,
                reference_id=ref_id or f"csv_{target_account_id}_{idempotency_hash[:8]}",
                balance_after=round(current_bal, 2),
                provenance=DataProvenance.CSV_IMPORT.value,
            )
            activities_to_insert.append(act_model)

            canonical = CanonicalTransaction(
                transaction_id=act_model.reference_id,
                account_id=target_account_id,
                amount=round(amt, 2),
                currency="BDT",
                direction=dir_enum,
                activity_type=ActivityType.MERCHANT_PAYMENT,
                timestamp_utc=parsed_dt,
                category=cat,
                channel=channel,
                counterparty_name=counterparty,
                reference_id=ref_id,
                balance_after=round(current_bal, 2),
                provenance=DataProvenance.CSV_IMPORT,
            )
            canonical_list.append(canonical)
            if ref_id:
                existing_refs.add(ref_id)

        # 3. Commit records & update user current balance
        if activities_to_insert:
            try:
                db.add_all(activities_to_insert)
                account.current_balance = round(current_bal, 2)
                db.commit()
                result.records_ingested = len(activities_to_insert)
                result.ingested_transactions = canonical_list

                # Invalidate forecast cache for target account
                forecast_cache.invalidate(target_account_id)
                try:
                    from app.api.spendable import get_spendable_service
                    get_spendable_service().invalidate_user_cache(target_account_id)
                except Exception:
                    pass
            except Exception as e:
                db.rollback()
                result.errors.append(f"Database commit failed: {str(e)}")
                result.records_ingested = 0

        return result
