"""Exploratory Data Analysis (EDA) Engine for Spendable synthetic datasets.

Performs dataset overview metrics, user-level statistical profiling,
persona differentiation sanity checks, recurring-pattern observable analysis,
and temporal dynamics analysis.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


class EDAEngine:
    """Exploratory Data Analysis engine for synthetic financial datasets."""

    def __init__(self, activities: List[Dict[str, Any]], ground_truth: Optional[Dict[str, Any]] = None):
        self.raw_activities = activities
        self.ground_truth = ground_truth or {}
        self.df = self._prepare_dataframe(activities)

    def _prepare_dataframe(self, activities: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert raw transaction list into a structured pandas DataFrame."""
        if not activities:
            return pd.DataFrame()

        rows = []
        for act in activities:
            row = dict(act)
            # Ensure float conversions for numerical pandas aggregations
            row["amount_num"] = float(Decimal(str(act["amount"])))
            bal = act.get("balance_after")
            row["balance_num"] = float(Decimal(str(bal))) if bal is not None else np.nan

            ts = act["timestamp_utc"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            row["timestamp_dt"] = ts
            row["date"] = ts.date()
            row["year_month"] = ts.strftime("%Y-%m")

            d_str = str(act["direction"]).replace("TransactionDirection.", "")
            t_str = str(act["activity_type"]).replace("ActivityType.", "")
            row["direction_clean"] = d_str
            row["type_clean"] = t_str

            rows.append(row)

        df = pd.DataFrame(rows)
        df.sort_values(by="timestamp_dt", inplace=True)
        return df

    def get_dataset_overview(self) -> Dict[str, Any]:
        """Compute top-level summary metrics across the entire dataset."""
        if self.df.empty:
            return {}

        total_users = self.df["account_id"].nunique()
        total_txns = len(self.df)
        min_date = self.df["timestamp_dt"].min()
        max_date = self.df["timestamp_dt"].max()
        duration_days = (max_date - min_date).days + 1

        txns_per_user = self.df.groupby("account_id").size()

        inflows = self.df[self.df["direction_clean"] == "INFLOW"]
        outflows = self.df[self.df["direction_clean"] == "OUTFLOW"]

        amounts = self.df["amount_num"]
        q25, q50, q75 = np.percentile(amounts, [25, 50, 75])

        balances = self.df["balance_num"].dropna()
        bal_q25, bal_q50, bal_q75 = np.percentile(balances, [25, 50, 75]) if not balances.empty else (0, 0, 0)

        # Monthly summary
        monthly = self.df.groupby(["year_month", "direction_clean"])["amount_num"].agg(["count", "sum"]).unstack(fill_value=0)
        
        monthly_summary = []
        months = sorted(self.df["year_month"].unique())
        for m in months:
            in_val = float(monthly.loc[m, ("sum", "INFLOW")]) if (m, ("sum", "INFLOW")) in monthly.columns else 0.0
            out_val = float(monthly.loc[m, ("sum", "OUTFLOW")]) if (m, ("sum", "OUTFLOW")) in monthly.columns else 0.0
            in_cnt = int(monthly.loc[m, ("count", "INFLOW")]) if (m, ("count", "INFLOW")) in monthly.columns else 0
            out_cnt = int(monthly.loc[m, ("count", "OUTFLOW")]) if (m, ("count", "OUTFLOW")) in monthly.columns else 0

            monthly_summary.append({
                "year_month": m,
                "inflow_count": in_cnt,
                "inflow_sum": round(in_val, 2),
                "outflow_count": out_cnt,
                "outflow_sum": round(out_val, 2),
                "total_txns": in_cnt + out_cnt,
                "net_cashflow": round(in_val - out_val, 2),
            })

        # Distributions
        type_dist = self.df.groupby("type_clean")["amount_num"].agg(["count", "sum"]).reset_index()
        type_dist["pct_count"] = (type_dist["count"] / total_txns * 100).round(2)
        type_dist["sum"] = type_dist["sum"].round(2)

        cat_dist = self.df.groupby("category")["amount_num"].agg(["count", "sum"]).reset_index()
        cat_dist["pct_count"] = (cat_dist["count"] / total_txns * 100).round(2)
        cat_dist["sum"] = cat_dist["sum"].round(2)

        channel_dist = self.df.groupby("channel")["amount_num"].agg(["count"]).reset_index()
        channel_dist["pct_count"] = (channel_dist["count"] / total_txns * 100).round(2)

        return {
            "total_users": total_users,
            "total_transactions": total_txns,
            "start_date": min_date.isoformat(),
            "end_date": max_date.isoformat(),
            "duration_days": duration_days,
            "user_activity": {
                "mean_txns_per_user": round(float(txns_per_user.mean()), 2),
                "median_txns_per_user": float(txns_per_user.median()),
                "min_txns_per_user": int(txns_per_user.min()),
                "max_txns_per_user": int(txns_per_user.max()),
                "std_txns_per_user": round(float(txns_per_user.std()), 2),
            },
            "inflows": {
                "count": len(inflows),
                "total_sum": round(float(inflows["amount_num"].sum()), 2),
                "mean_amount": round(float(inflows["amount_num"].mean()), 2) if not inflows.empty else 0.0,
                "median_amount": round(float(inflows["amount_num"].median()), 2) if not inflows.empty else 0.0,
            },
            "outflows": {
                "count": len(outflows),
                "total_sum": round(float(outflows["amount_num"].sum()), 2),
                "mean_amount": round(float(outflows["amount_num"].mean()), 2) if not outflows.empty else 0.0,
                "median_amount": round(float(outflows["amount_num"].median()), 2) if not outflows.empty else 0.0,
            },
            "amount_stats": {
                "mean": round(float(amounts.mean()), 2),
                "std": round(float(amounts.std()), 2),
                "median": round(float(np.median(amounts)), 2),
                "min": round(float(amounts.min()), 2),
                "max": round(float(amounts.max()), 2),
                "q25": round(float(q25), 2),
                "q75": round(float(q75), 2),
                "iqr": round(float(q75 - q25), 2),
            },
            "balance_stats": {
                "mean": round(float(balances.mean()), 2) if not balances.empty else 0.0,
                "median": round(float(np.median(balances)), 2) if not balances.empty else 0.0,
                "min": round(float(balances.min()), 2) if not balances.empty else 0.0,
                "max": round(float(balances.max()), 2) if not balances.empty else 0.0,
                "q25": round(float(bal_q25), 2),
                "q75": round(float(bal_q75), 2),
            },
            "type_distribution": type_dist.to_dict(orient="records"),
            "category_distribution": cat_dist.to_dict(orient="records"),
            "channel_distribution": channel_dist.to_dict(orient="records"),
            "monthly_summary": monthly_summary,
        }

    def get_user_level_metrics(self) -> List[Dict[str, Any]]:
        """Compute per-user statistical summary metrics."""
        if self.df.empty:
            return []

        user_metrics = []
        gt_users = self.ground_truth.get("users", {})

        for uid, user_df in self.df.groupby("account_id"):
            user_gt = gt_users.get(uid, {})
            persona = user_gt.get("persona", "UNKNOWN")

            in_df = user_df[user_df["direction_clean"] == "INFLOW"]
            out_df = user_df[user_df["direction_clean"] == "OUTFLOW"]

            total_in = float(in_df["amount_num"].sum())
            total_out = float(out_df["amount_num"].sum())
            net_cf = total_in - total_out

            bals = user_df["balance_num"].dropna()
            min_bal = float(bals.min()) if not bals.empty else 0.0
            max_bal = float(bals.max()) if not bals.empty else 0.0
            latest_bal = float(user_df.iloc[-1]["balance_num"]) if not bals.empty else 0.0
            start_bal = float(user_gt.get("starting_balance", 0.0))

            user_metrics.append({
                "account_id": uid,
                "persona": str(persona),
                "total_txns": len(user_df),
                "total_inflow": round(total_in, 2),
                "total_outflow": round(total_out, 2),
                "net_cashflow": round(net_cf, 2),
                "mean_txn_amount": round(float(user_df["amount_num"].mean()), 2),
                "median_txn_amount": round(float(user_df["amount_num"].median()), 2),
                "starting_balance": round(start_bal, 2),
                "latest_balance": round(latest_bal, 2),
                "min_observed_balance": round(min_bal, 2),
                "max_observed_balance": round(max_bal, 2),
            })

        return user_metrics

    def get_persona_sanity_check(self) -> Dict[str, Any]:
        """Group statistics by persona to verify behavioral differentiation."""
        if self.df.empty:
            return {}

        # Merge persona from ground truth if available
        gt_users = self.ground_truth.get("users", {})
        df_copy = self.df.copy()
        df_copy["persona"] = df_copy["account_id"].map(lambda uid: str(gt_users.get(uid, {}).get("persona", "UNKNOWN")))

        persona_stats = {}
        for persona, p_df in df_copy.groupby("persona"):
            user_count = p_df["account_id"].nunique()
            txns_per_user = len(p_df) / user_count if user_count > 0 else 0

            in_df = p_df[p_df["direction_clean"] == "INFLOW"]
            out_df = p_df[p_df["direction_clean"] == "OUTFLOW"]

            avg_inflow_per_user = float(in_df["amount_num"].sum()) / user_count if user_count > 0 else 0.0
            avg_outflow_per_user = float(out_df["amount_num"].sum()) / user_count if user_count > 0 else 0.0
            net_cf_per_user = avg_inflow_per_user - avg_outflow_per_user

            bals = p_df["balance_num"].dropna()
            min_bal = float(bals.min()) if not bals.empty else 0.0
            bal_volatility = float(p_df.groupby("account_id")["balance_num"].std().mean()) if user_count > 0 else 0.0

            persona_stats[persona] = {
                "user_count": user_count,
                "total_txns": len(p_df),
                "avg_txns_per_user": round(txns_per_user, 1),
                "avg_inflow_per_user": round(avg_inflow_per_user, 2),
                "avg_outflow_per_user": round(avg_outflow_per_user, 2),
                "avg_net_cashflow_per_user": round(net_cf_per_user, 2),
                "min_balance_observed": round(min_bal, 2),
                "avg_balance_volatility_std": round(bal_volatility, 2),
            }

        return persona_stats

    def get_recurring_pattern_sanity_check(self) -> Dict[str, Any]:
        """Inspect observable repeated transactions to same counterparty for recurrence evidence."""
        if self.df.empty:
            return {}

        # Group by account_id and counterparty_name to detect observable recurring candidates
        observable_patterns = []

        for (uid, cp_name), cp_df in self.df.groupby(["account_id", "counterparty_name"]):
            if len(cp_df) >= 2 and cp_name:
                cp_df_sorted = cp_df.sort_values(by="timestamp_dt")
                time_diffs = cp_df_sorted["timestamp_dt"].diff().dropna()
                days_between = time_diffs.dt.total_seconds() / (24 * 3600)

                amounts = cp_df_sorted["amount_num"]
                avg_amt = float(amounts.mean())
                std_amt = float(amounts.std()) if len(amounts) > 1 else 0.0
                mean_interval = float(days_between.mean()) if not time_diffs.empty else 0.0

                observable_patterns.append({
                    "account_id": uid,
                    "counterparty_name": cp_name,
                    "category": str(cp_df_sorted.iloc[0]["category"]),
                    "occurrences": len(cp_df),
                    "mean_interval_days": round(mean_interval, 1),
                    "mean_amount": round(avg_amt, 2),
                    "amount_std": round(std_amt, 2),
                })

        # Count how many planted rules in ground truth are observably detected in transaction history
        gt_users = self.ground_truth.get("users", {})
        total_planted = 0
        observed_planted = 0

        for uid, u_gt in gt_users.items():
            for rule in u_gt.get("planted_rules", []):
                total_planted += 1
                rule_cp = rule.get("counterparty_name")
                if rule_cp:
                    matches = self.df[(self.df["account_id"] == uid) & (self.df["counterparty_name"] == rule_cp)]
                    if len(matches) >= 2:
                        observed_planted += 1

        return {
            "total_observable_repeated_streams": len(observable_patterns),
            "sample_repeated_streams": observable_patterns[:15],
            "ground_truth_planted_rules_count": total_planted,
            "observable_planted_rules_count": observed_planted,
            "planted_rule_detection_rate_pct": round(observed_planted / total_planted * 100, 1) if total_planted > 0 else 0.0,
        }
