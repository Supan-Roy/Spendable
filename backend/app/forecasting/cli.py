"""Command Line Interface for Cash-Flow Forecasting & Model Comparison.

Usage:
    python -m app.forecasting.cli --dataset-dir data/ --safety-threshold 15000
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
import pandas as pd

from app.forecasting.baselines import (
    RecurringCommitmentBaseline,
    RollingAverageBaseline,
)
from app.forecasting.evaluator import ForecastingEvaluator
from app.forecasting.models import CashFlowForecastModel
from app.forecasting.pipeline import ForecastingPipeline
from app.forecasting.schema import ForecastConfig, ForecastingReport


def main():
    parser = argparse.ArgumentParser(description="Spendable Cash-Flow Forecasting CLI")
    parser.add_argument("--dataset-dir", type=str, default="data/", help="Path to data directory")
    parser.add_argument("--safety-threshold", type=float, default=15000.0, help="Low-balance safety threshold in BDT")
    parser.add_argument("--output-json", type=str, default="reports/forecasting_evaluation.json", help="Output path for evaluation report")

    args = parser.parse_args()
    dataset_dir = Path(args.dataset_dir)

    print(f"==================================================")
    print(f"SPENDABLE CASH-FLOW FORECASTING & LIQUIDITY EVALUATION")
    print(f"Dataset Directory: {dataset_dir}")
    print(f"Safety Threshold : {args.safety_threshold:,.2f} BDT")
    print(f"==================================================\n")

    pipeline = ForecastingPipeline(str(dataset_dir))
    df_train, df_val, df_test = pipeline.load_feature_splits()

    print(f"Loaded Feature Matrix Splits:")
    print(f"  TRAIN     : {len(df_train):,} snapshot rows")
    print(f"  VALIDATION: {len(df_val):,} snapshot rows")
    print(f"  TEST      : {len(df_test):,} snapshot rows\n")

    # Load ground truth for persona breakdown
    gt_path = dataset_dir / "ground_truth.json"
    gt_data = {}
    if gt_path.exists():
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

    # Initialize baselines & ML model
    base_rolling = RollingAverageBaseline()
    base_recurring = RecurringCommitmentBaseline()
    ml_model = CashFlowForecastModel(random_seed=42)

    print("Fitting Supervised ML Model (HistGradientBoostingRegressor)...")
    ml_model.fit(df_train)
    print("ML Model training completed successfully!\n")

    evaluator = ForecastingEvaluator(safety_threshold_bdt=args.safety_threshold)

    # Evaluate models on VALIDATION split (for model selection)
    print("--- VALIDATION SET MODEL COMPARISON ---")
    val_rolling = evaluator.evaluate_model(base_rolling, df_val, "VALIDATION", gt_data)
    val_recurring = evaluator.evaluate_model(base_recurring, df_val, "VALIDATION", gt_data)
    val_ml = evaluator.evaluate_model(ml_model, df_val, "VALIDATION", gt_data)

    models_val = [val_rolling, val_recurring, val_ml]
    
    print(f"{'Model Name':<30} | {'Horizon':<7} | {'MAE (BDT)':<12} | {'RMSE (BDT)':<12} | {'R2 Score':<8} | {'Pressure F1':<11}")
    print("-" * 92)

    for m in models_val:
        for H, reg_m in zip((7, 14, 30), (m.metrics_7d, m.metrics_14d, m.metrics_30d)):
            p_f1 = m.pressure_metrics_30d.f1_score if H == 30 else "-"
            print(f"{m.model_name:<30} | {H}d     | {reg_m.mae:<12,.2f} | {reg_m.rmse:<12,.2f} | {reg_m.r2_score:<8.4f} | {str(p_f1):<11}")
        print("-" * 92)

    # Evaluate final selected model (ML Model) on TEST split
    print("\n--- FINAL UNBIASED TEST SET EVALUATION (SELECTED MODEL: ML) ---")
    test_ml = evaluator.evaluate_model(ml_model, df_test, "TEST", gt_data)

    print(f"{'Horizon':<8} | {'MAE (BDT)':<12} | {'RMSE (BDT)':<12} | {'R2 Score':<8} | {'Pressure Prec':<13} | {'Pressure Rec':<12} | {'Pressure F1':<11}")
    print("-" * 92)
    for H, reg_m in zip((7, 14, 30), (test_ml.metrics_7d, test_ml.metrics_14d, test_ml.metrics_30d)):
        p_prec = test_ml.pressure_metrics_30d.precision if H == 30 else "-"
        p_rec = test_ml.pressure_metrics_30d.recall if H == 30 else "-"
        p_f1 = test_ml.pressure_metrics_30d.f1_score if H == 30 else "-"
        print(f"{H}d       | {reg_m.mae:<12,.2f} | {reg_m.rmse:<12,.2f} | {reg_m.r2_score:<8.4f} | {str(p_prec):<13} | {str(p_rec):<12} | {str(p_f1):<11}")
    print("-" * 92)

    # Persona breakdown on TEST
    print("\n--- TEST SET PERSONA PERFORMANCE BREAKDOWN (30-DAY MINIMUM BALANCE) ---")
    print(f"{'Persona Profile':<25} | {'Snapshots':<10} | {'MAE 30d (BDT)':<14} | {'RMSE 30d (BDT)':<15} | {'Pressure F1':<11}")
    print("-" * 84)
    for pm in test_ml.persona_breakdown:
        print(f"{pm.persona:<25} | {pm.total_snapshots:<10} | {pm.mae_30d:<14,.2f} | {pm.rmse_30d:<15,.2f} | {pm.pressure_f1_30d:<11.4f}")
    print("-" * 84)

    # Compute Feature Importances
    feat_imp = evaluator.compute_feature_importance(ml_model, df_val, horizon_days=30, top_n=10)
    print("\n--- TOP 10 FEATURE IMPORTANCES (30-DAY MINIMUM BALANCE) ---")
    for rank, (feat, imp) in enumerate(feat_imp.items(), 1):
        print(f" {rank:2d}. {feat:<32} : {imp:,.4f}")

    # Build report
    config = ForecastConfig(safety_threshold_bdt=args.safety_threshold)
    report = ForecastingReport(
        evaluated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        config=config,
        models_evaluated=[m.model_name for m in models_val],
        summaries=models_val + [test_ml],
        feature_importances=feat_imp,
    )

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    print(f"\nForecasting evaluation report successfully saved to: {output_path}")


if __name__ == "__main__":
    main()
