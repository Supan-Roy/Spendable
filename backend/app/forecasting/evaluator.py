"""Evaluation engine for cash-flow forecasting models.

Computes multi-horizon regression metrics (MAE, RMSE, R2), low-balance liquidity pressure
detection precision & recall, persona-level error breakdowns, and permutation feature importances.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.forecasting.schema import (
    ForecastConfig,
    ForecastingReport,
    HorizonForecast,
    LiquidityPressureMetric,
    ModelEvaluationSummary,
    PersonaEvaluationMetric,
    RegressionMetric,
)


class ForecastingEvaluator:
    """Evaluates forecasting models on regression metrics, liquidity pressure, and user personas."""

    def __init__(self, safety_threshold_bdt: float = 15000.0):
        self.safety_threshold_bdt = safety_threshold_bdt

    def evaluate_model(
        self,
        model: Any,
        df_split: pd.DataFrame,
        split_name: str,
        gt_data: Optional[Dict[str, Any]] = None,
    ) -> ModelEvaluationSummary:
        """Evaluate a forecasting model or baseline on a specific dataset split."""
        split_name_upper = split_name.upper()
        n_snapshots = len(df_split)

        # Prepare persona map if ground truth available
        user_personas: Dict[str, str] = {}
        if gt_data and "users" in gt_data:
            for uid, uinfo in gt_data["users"].items():
                user_personas[uid] = str(uinfo.get("persona", "UNKNOWN")).upper()

        reg_metrics: Dict[int, RegressionMetric] = {}
        pressure_metrics_30d: Optional[LiquidityPressureMetric] = None

        # Predict across all snapshots
        preds_min: Dict[int, List[float]] = {7: [], 14: [], 30: []}
        targets_min: Dict[int, List[float]] = {7: [], 14: [], 30: []}

        for idx, row in df_split.iterrows():
            row_dict = row.to_dict()
            f_out = model.predict_snapshot(row_dict, safety_threshold_bdt=self.safety_threshold_bdt)

            for H in (7, 14, 30):
                target_col = f"target_future_min_balance_{H}d"
                t_val = float(row.get(target_col, row.get("current_balance", 0.0)))
                p_val = float(getattr(f_out, f"forecast_{H}d").minimum_projected_balance)

                preds_min[H].append(p_val)
                targets_min[H].append(t_val)

        # Compute regression metrics per horizon
        for H in (7, 14, 30):
            y_true = np.array(targets_min[H])
            y_pred = np.array(preds_min[H])

            mae = float(mean_absolute_error(y_true, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
            r2 = float(r2_score(y_true, y_pred)) if np.var(y_true) > 0 else 0.0

            reg_metrics[H] = RegressionMetric(
                horizon_days=H,
                mae=round(mae, 2),
                rmse=round(rmse, 2),
                r2_score=round(r2, 4),
            )

        # Compute 30d Liquidity Pressure Metrics
        y_true_30d = np.array(targets_min[30])
        y_pred_30d = np.array(preds_min[30])

        actual_pressure = (y_true_30d < self.safety_threshold_bdt)
        pred_pressure = (y_pred_30d < self.safety_threshold_bdt)

        tp = int(np.sum(actual_pressure & pred_pressure))
        fp = int(np.sum((~actual_pressure) & pred_pressure))
        fn = int(np.sum(actual_pressure & (~pred_pressure)))
        tn = int(np.sum((~actual_pressure) & (~pred_pressure)))

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        pressure_metrics_30d = LiquidityPressureMetric(
            horizon_days=30,
            safety_threshold_bdt=self.safety_threshold_bdt,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
        )

        # Persona breakdown evaluation
        persona_breakdown = self._evaluate_persona_breakdown(
            df_split=df_split,
            preds_min_30d=preds_min[30],
            targets_min_30d=targets_min[30],
            user_personas=user_personas,
        )

        model_name_str = getattr(model, "model_name", str(type(model).__name__))

        return ModelEvaluationSummary(
            model_name=model_name_str,
            split_name=split_name_upper,
            total_snapshots=n_snapshots,
            metrics_7d=reg_metrics[7],
            metrics_14d=reg_metrics[14],
            metrics_30d=reg_metrics[30],
            pressure_metrics_30d=pressure_metrics_30d,
            persona_breakdown=persona_breakdown,
        )

    def _evaluate_persona_breakdown(
        self,
        df_split: pd.DataFrame,
        preds_min_30d: List[float],
        targets_min_30d: List[float],
        user_personas: Dict[str, str],
    ) -> List[PersonaEvaluationMetric]:
        """Compute performance breakdown by user persona."""
        persona_indices: Dict[str, List[int]] = {}

        for idx, row in df_split.reset_index(drop=True).iterrows():
            uid = str(row.get("account_id") or row.get("user_id") or "")
            persona = user_personas.get(uid, str(row.get("persona", "DEFAULT"))).upper()
            if persona not in persona_indices:
                persona_indices[persona] = []
            persona_indices[persona].append(idx)

        metrics: List[PersonaEvaluationMetric] = []
        for persona, idxs in sorted(persona_indices.items()):
            if not idxs:
                continue
            y_t = np.array([targets_min_30d[i] for i in idxs])
            y_p = np.array([preds_min_30d[i] for i in idxs])

            mae = float(mean_absolute_error(y_t, y_p))
            rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))

            actual_press = (y_t < self.safety_threshold_bdt)
            pred_press = (y_p < self.safety_threshold_bdt)
            tp = int(np.sum(actual_press & pred_press))
            fp = int(np.sum((~actual_press) & pred_press))
            fn = int(np.sum(actual_press & (~pred_press)))
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            metrics.append(
                PersonaEvaluationMetric(
                    persona=persona,
                    total_snapshots=len(idxs),
                    mae_30d=round(mae, 2),
                    rmse_30d=round(rmse, 2),
                    pressure_f1_30d=round(f1, 4),
                )
            )

        return metrics

    def compute_feature_importance(
        self,
        ml_model: Any,
        df_val: pd.DataFrame,
        horizon_days: int = 30,
        top_n: int = 15,
    ) -> Dict[str, float]:
        """Compute permutation feature importances for the ML model on validation split."""
        if not hasattr(ml_model, "models_min_bal") or not ml_model.is_fitted:
            return {}

        estimator = ml_model.models_min_bal[horizon_days]
        feature_cols = ml_model.feature_cols
        target_col = f"target_future_min_balance_{horizon_days}d"

        if target_col not in df_val.columns:
            return {}

        X_val = df_val[feature_cols].fillna(0.0).values
        y_val = df_val[target_col].fillna(0.0).values

        res = permutation_importance(
            estimator, X_val, y_val, n_repeats=5, random_state=ml_model.random_seed
        )

        importances = {}
        for col, imp in zip(feature_cols, res.importances_mean):
            importances[col] = float(imp)

        # Sort top N features
        sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True)[:top_n])
        return sorted_imp
