"""Core Point-in-Time Feature Builder for Spendable.

Calculates leakage-safe financial features for a user at an exact snapshot timestamp T.
Features are calculated strictly from transactions occurring at or before snapshot T.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional


class FeatureBuilder:
    """Point-in-Time Feature Extraction Engine."""

    def __init__(self, user_activities: List[Dict[str, Any]]):
        """Initialize builder with a single user's raw transaction records.
        
        Args:
            user_activities: Transaction records belonging to ONE user, ordered by timestamp_utc.
        """
        self.user_activities = sorted(user_activities, key=lambda x: self._parse_timestamp(x["timestamp_utc"]))

    @staticmethod
    def _parse_timestamp(ts: Any) -> datetime:
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts.astimezone(timezone.utc)
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        raise TypeError(f"Invalid timestamp type: {type(ts)}")

    def build_snapshot_features(self, snapshot_time: datetime) -> Dict[str, Any]:
        """Compute snapshot feature dictionary at timestamp snapshot_time.
        
        Guarantees STRICT ZERO LEAKAGE: transactions occurring after snapshot_time are ignored.
        """
        st_utc = self._parse_timestamp(snapshot_time)

        # 1. Filter strictly past transactions: t <= snapshot_time
        past_acts = [
            a for a in self.user_activities
            if self._parse_timestamp(a["timestamp_utc"]) <= st_utc
        ]

        if not past_acts:
            # User has no history prior to snapshot_time
            return self._build_empty_feature_dict(st_utc)

        account_id = past_acts[0]["account_id"]
        latest_act = past_acts[-1]
        current_balance = float(Decimal(str(latest_act.get("balance_after", 0.0))))

        # 2. Window filtering
        t_7d = st_utc - timedelta(days=7)
        t_14d = st_utc - timedelta(days=14)
        t_30d = st_utc - timedelta(days=30)

        acts_7d = [a for a in past_acts if self._parse_timestamp(a["timestamp_utc"]) >= t_7d]
        acts_14d = [a for a in past_acts if self._parse_timestamp(a["timestamp_utc"]) >= t_14d]
        acts_30d = [a for a in past_acts if self._parse_timestamp(a["timestamp_utc"]) >= t_30d]

        # 3. Liquidity Features
        b_7d = [float(Decimal(str(a["balance_after"]))) for a in acts_7d if a.get("balance_after") is not None]
        b_14d = [float(Decimal(str(a["balance_after"]))) for a in acts_14d if a.get("balance_after") is not None]
        b_30d = [float(Decimal(str(a["balance_after"]))) for a in acts_30d if a.get("balance_after") is not None]

        bal_min_7d = min(b_7d) if b_7d else current_balance
        bal_min_14d = min(b_14d) if b_14d else current_balance
        bal_min_30d = min(b_30d) if b_30d else current_balance
        bal_max_30d = max(b_30d) if b_30d else current_balance
        bal_mean_30d = float(np.mean(b_30d)) if b_30d else current_balance
        bal_std_30d = float(np.std(b_30d)) if len(b_30d) > 1 else 0.0

        bal_change_7d = current_balance - (b_7d[0] if b_7d else current_balance)
        bal_change_30d = current_balance - (b_30d[0] if b_30d else current_balance)

        # 4. Inflow & Outflow Splitting
        inflows_7d = [a for a in acts_7d if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"]
        inflows_14d = [a for a in acts_14d if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"]
        inflows_30d = [a for a in acts_30d if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"]

        outflows_7d = [a for a in acts_7d if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"]
        outflows_14d = [a for a in acts_14d if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"]
        outflows_30d = [a for a in acts_30d if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"]

        # Inflow Metrics
        tot_inflow_7d = sum(float(Decimal(str(a["amount"]))) for a in inflows_7d)
        tot_inflow_14d = sum(float(Decimal(str(a["amount"]))) for a in inflows_14d)
        tot_inflow_30d = sum(float(Decimal(str(a["amount"]))) for a in inflows_30d)

        in_cnt_30d = len(inflows_30d)
        in_amts_30d = [float(Decimal(str(a["amount"]))) for a in inflows_30d]
        avg_inflow_30d = float(np.mean(in_amts_30d)) if in_amts_30d else 0.0
        inflow_vol_30d = float(np.std(in_amts_30d)) if len(in_amts_30d) > 1 else 0.0

        all_past_inflows = [a for a in past_acts if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"]
        if all_past_inflows:
            last_in_ts = self._parse_timestamp(all_past_inflows[-1]["timestamp_utc"])
            days_since_last_inflow = round((st_utc - last_in_ts).total_seconds() / 86400.0, 2)
        else:
            days_since_last_inflow = 999.0

        # Outflow Metrics
        tot_outflow_7d = sum(float(Decimal(str(a["amount"]))) for a in outflows_7d)
        tot_outflow_14d = sum(float(Decimal(str(a["amount"]))) for a in outflows_14d)
        tot_outflow_30d = sum(float(Decimal(str(a["amount"]))) for a in outflows_30d)

        out_cnt_30d = len(outflows_30d)
        out_amts_30d = [float(Decimal(str(a["amount"]))) for a in outflows_30d]
        avg_outflow_30d = float(np.mean(out_amts_30d)) if out_amts_30d else 0.0
        med_outflow_30d = float(np.median(out_amts_30d)) if out_amts_30d else 0.0
        spending_vol_30d = float(np.std(out_amts_30d)) if len(out_amts_30d) > 1 else 0.0

        all_past_outflows = [a for a in past_acts if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"]
        if all_past_outflows:
            last_out_ts = self._parse_timestamp(all_past_outflows[-1]["timestamp_utc"])
            days_since_last_outflow = round((st_utc - last_out_ts).total_seconds() / 86400.0, 2)
        else:
            days_since_last_outflow = 999.0

        # 5. Cash Flow & Ratios
        net_cf_7d = tot_inflow_7d - tot_outflow_7d
        net_cf_14d = tot_inflow_14d - tot_outflow_14d
        net_cf_30d = tot_inflow_30d - tot_outflow_30d

        in_out_ratio_30d = tot_inflow_30d / (tot_outflow_30d + 1e-5)
        avg_daily_net_flow_30d = net_cf_30d / 30.0

        # 6. Spending Behavior & Concentration
        all_amts_30d = [float(Decimal(str(a["amount"]))) for a in acts_30d]
        avg_txn_amt_30d = float(np.mean(all_amts_30d)) if all_amts_30d else 0.0
        med_txn_amt_30d = float(np.median(all_amts_30d)) if all_amts_30d else 0.0
        txn_freq_30d = len(acts_30d) / 30.0

        essential_cats = {"HOUSING", "UTILITIES", "TELECOM"}
        discretionary_cats = {"DINING", "FOOD_AND_GROCERIES", "DISCRETIONARY_SHOPPING", "ENTERTAINMENT"}

        essential_sum = sum(float(Decimal(str(a["amount"]))) for a in outflows_30d if a.get("category") in essential_cats)
        discretionary_sum = sum(float(Decimal(str(a["amount"]))) for a in outflows_30d if a.get("category") in discretionary_cats)

        essential_share_30d = essential_sum / (tot_outflow_30d + 1e-5)
        discretionary_share_30d = discretionary_sum / (tot_outflow_30d + 1e-5)

        # Herfindahl-Hirschman Category Concentration Index
        cat_sums: Dict[str, float] = {}
        for a in outflows_30d:
            cat = a.get("category", "OTHER") or "OTHER"
            cat_sums[cat] = cat_sums.get(cat, 0.0) + float(Decimal(str(a["amount"])))

        if cat_sums and tot_outflow_30d > 0:
            cat_shares = [c_amt / tot_outflow_30d for c_amt in cat_sums.values()]
            cat_hhi_30d = float(sum(s ** 2 for s in cat_shares))
        else:
            cat_hhi_30d = 1.0

        # 7. Balance Pressure Features
        low_bal_count = sum(1 for a in acts_30d if float(Decimal(str(a.get("balance_after", 0)))) < 1000.0)
        low_bal_ratio_30d = low_bal_count / max(1, len(acts_30d))

        drawdown_30d = (bal_max_30d - current_balance) / (bal_max_30d + 1e-5)

        # Linear regression slope of balance vs day offset in 30d window
        if len(acts_30d) >= 3:
            day_offsets = [(self._parse_timestamp(a["timestamp_utc"]) - t_30d).total_seconds() / 86400.0 for a in acts_30d]
            b_vals = [float(Decimal(str(a["balance_after"]))) for a in acts_30d]
            try:
                slope, _ = np.polyfit(day_offsets, b_vals, 1)
                trend_slope_30d = float(slope)
            except Exception:
                trend_slope_30d = 0.0
        else:
            trend_slope_30d = 0.0

        # 8. Time of Day & Temporal Features
        snapshot_hour = st_utc.hour
        snapshot_dow = st_utc.weekday()
        snapshot_is_weekend = 1 if snapshot_dow >= 5 else 0

        outflow_hours = [self._parse_timestamp(a["timestamp_utc"]).hour for a in outflows_30d]
        avg_outflow_hour_30d = float(np.mean(outflow_hours)) if outflow_hours else 12.0

        return {
            "account_id": account_id,
            "snapshot_time": st_utc.isoformat(),
            # Temporal / Time Features
            "snapshot_hour_of_day": snapshot_hour,
            "snapshot_day_of_week": snapshot_dow,
            "snapshot_is_weekend": snapshot_is_weekend,
            "avg_outflow_hour_30d": round(avg_outflow_hour_30d, 2),
            # Liquidity
            "current_balance": round(current_balance, 2),
            "balance_min_7d": round(bal_min_7d, 2),
            "balance_min_14d": round(bal_min_14d, 2),
            "balance_min_30d": round(bal_min_30d, 2),
            "balance_max_30d": round(bal_max_30d, 2),
            "balance_mean_30d": round(bal_mean_30d, 2),
            "balance_std_30d": round(bal_std_30d, 2),
            "balance_change_7d": round(bal_change_7d, 2),
            "balance_change_30d": round(bal_change_30d, 2),
            # Inflow
            "total_inflow_7d": round(tot_inflow_7d, 2),
            "total_inflow_14d": round(tot_inflow_14d, 2),
            "total_inflow_30d": round(tot_inflow_30d, 2),
            "inflow_count_30d": in_cnt_30d,
            "avg_inflow_amount_30d": round(avg_inflow_30d, 2),
            "days_since_last_inflow": round(days_since_last_inflow, 2),
            "inflow_volatility_30d": round(inflow_vol_30d, 2),
            # Outflow
            "total_outflow_7d": round(tot_outflow_7d, 2),
            "total_outflow_14d": round(tot_outflow_14d, 2),
            "total_outflow_30d": round(tot_outflow_30d, 2),
            "outflow_count_30d": out_cnt_30d,
            "avg_outflow_amount_30d": round(avg_outflow_30d, 2),
            "median_outflow_amount_30d": round(med_outflow_30d, 2),
            "days_since_last_outflow": round(days_since_last_outflow, 2),
            "spending_volatility_30d": round(spending_vol_30d, 2),
            # Cash Flow
            "net_cash_flow_7d": round(net_cf_7d, 2),
            "net_cash_flow_14d": round(net_cf_14d, 2),
            "net_cash_flow_30d": round(net_cf_30d, 2),
            "inflow_outflow_ratio_30d": round(in_out_ratio_30d, 4),
            "avg_daily_net_flow_30d": round(avg_daily_net_flow_30d, 2),
            # Spending Behavior
            "avg_transaction_amount_30d": round(avg_txn_amt_30d, 2),
            "median_transaction_amount_30d": round(med_txn_amt_30d, 2),
            "transaction_frequency_30d": round(txn_freq_30d, 4),
            "essential_spending_share_30d": round(essential_share_30d, 4),
            "discretionary_spending_share_30d": round(discretionary_share_30d, 4),
            "category_concentration_index_30d": round(cat_hhi_30d, 4),
            # Balance Pressure
            "low_balance_days_ratio_30d": round(low_bal_ratio_30d, 4),
            "drawdown_from_recent_max_30d": round(drawdown_30d, 4),
            "recent_balance_trend_slope": round(trend_slope_30d, 4),
        }

    def _build_empty_feature_dict(self, snapshot_time: datetime) -> Dict[str, Any]:
        """Return zero default feature vector if no past transactions exist prior to snapshot."""
        st_utc = self._parse_timestamp(snapshot_time)
        return {
            "account_id": self.user_activities[0]["account_id"] if self.user_activities else "UNKNOWN",
            "snapshot_time": st_utc.isoformat(),
            "snapshot_hour_of_day": st_utc.hour,
            "snapshot_day_of_week": st_utc.weekday(),
            "snapshot_is_weekend": 1 if st_utc.weekday() >= 5 else 0,
            "avg_outflow_hour_30d": 12.0,
            "current_balance": 0.0,
            "balance_min_7d": 0.0,
            "balance_min_14d": 0.0,
            "balance_min_30d": 0.0,
            "balance_max_30d": 0.0,
            "balance_mean_30d": 0.0,
            "balance_std_30d": 0.0,
            "balance_change_7d": 0.0,
            "balance_change_30d": 0.0,
            "total_inflow_7d": 0.0,
            "total_inflow_14d": 0.0,
            "total_inflow_30d": 0.0,
            "inflow_count_30d": 0,
            "avg_inflow_amount_30d": 0.0,
            "days_since_last_inflow": 999.0,
            "inflow_volatility_30d": 0.0,
            "total_outflow_7d": 0.0,
            "total_outflow_14d": 0.0,
            "total_outflow_30d": 0.0,
            "outflow_count_30d": 0,
            "avg_outflow_amount_30d": 0.0,
            "median_outflow_amount_30d": 0.0,
            "days_since_last_outflow": 999.0,
            "spending_volatility_30d": 0.0,
            "net_cash_flow_7d": 0.0,
            "net_cash_flow_14d": 0.0,
            "net_cash_flow_30d": 0.0,
            "inflow_outflow_ratio_30d": 0.0,
            "avg_daily_net_flow_30d": 0.0,
            "avg_transaction_amount_30d": 0.0,
            "median_transaction_amount_30d": 0.0,
            "transaction_frequency_30d": 0.0,
            "essential_spending_share_30d": 0.0,
            "discretionary_spending_share_30d": 0.0,
            "category_concentration_index_30d": 1.0,
            "low_balance_days_ratio_30d": 0.0,
            "drawdown_from_recent_max_30d": 0.0,
            "recent_balance_trend_slope": 0.0,
        }
