"""Command-line interface for Spendable Financial Intelligence Engine evaluation and backtesting.

Usage:
    python -m app.engine.cli --output-report reports/spendable_engine_evaluation.json
"""

import argparse
import json
from pathlib import Path
import pandas as pd

from app.config import settings
from app.engine.backtest import SpendableBacktester
from app.engine.calculator import SpendableCalculator
from app.forecasting.models import CashFlowForecastModel


def main():
    parser = argparse.ArgumentParser(description="Spendable Engine Backtesting Runner")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/processed",
        help="Path to processed data directory containing snapshots",
    )
    parser.add_argument(
        "--output-report",
        type=str,
        default="reports/spendable_engine_evaluation.json",
        help="Path to output JSON evaluation report",
    )
    args = parser.parse_args()

    data_path = Path(args.data_dir)
    print(f"Loading snapshot splits from {data_path}...")

    def load_split(name: str) -> Optional[pd.DataFrame]:
        for candidate in [
            data_path / f"features_{name}.csv",
            data_path / f"snapshots_{name}.parquet",
            data_path / f"{name}.csv",
            Path("data/features") / f"features_{name}.csv",
        ]:
            if candidate.exists():
                print(f"Found {name} split at {candidate}")
                if candidate.suffix == ".parquet":
                    return pd.read_parquet(candidate)
                else:
                    return pd.read_csv(candidate)
        return None

    df_train = load_split("train")
    df_val = load_split("validation")
    if df_val is None:
        df_val = load_split("val")
    df_test = load_split("test")

    # Fit forecasting model on train for evaluation
    model = CashFlowForecastModel()
    if df_train is not None:
        print("Training CashFlowForecastModel model for Spendable engine...")
        model.fit(df_train)

    forecast_models = {"model": model}

    # Load ground truth if present
    gt_candidates = [
        data_path / "ground_truth.json",
        Path("data") / "ground_truth.json",
        data_path / "synthetic_ground_truth.json",
    ]
    gt_data = None
    for gtp in gt_candidates:
        if gtp.exists():
            print(f"Found ground truth at {gtp}")
            with open(gtp, "r", encoding="utf-8") as f:
                gt_data = json.load(f)
            break

    backtester = SpendableBacktester()

    reports = {}
    for name, df in [("train", df_train), ("validation", df_val), ("test", df_test)]:
        if df is not None:
            print(f"Backtesting candidate methodologies on {name} split ({len(df)} snapshots)...")
            report = backtester.backtest_split(
                df_split=df,
                split_name=name,
                forecast_models=forecast_models,
                gt_data=gt_data,
            )
            reports[name] = report.model_dump()

    output_file = Path(args.output_report)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

    print(f"Successfully generated Spendable Engine backtest report at: {output_file}")


if __name__ == "__main__":
    main()
