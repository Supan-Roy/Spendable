"""Command-line interface for Recommendation & Explanation Engine evaluation.

Usage:
    python -m app.explanation.cli --output-report reports/recommendation_explanation_evaluation.json
"""

import argparse
import json
from pathlib import Path
from typing import Optional
import pandas as pd

from app.engine.calculator import SpendableCalculator
from app.recommendation.engine import RecommendationEngine
from app.scenario.simulator import ScenarioSimulator
from app.scenario.schema import ScenarioInput, ScenarioType
from app.explanation.gemini import ExplanationGenerator
from app.forecasting.models import CashFlowForecastModel


def main():
    parser = argparse.ArgumentParser(description="Recommendation & Explanation Evaluation Runner")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/features",
        help="Path to dataset directory containing features",
    )
    parser.add_argument(
        "--output-report",
        type=str,
        default="reports/recommendation_explanation_evaluation.json",
        help="Path to output JSON evaluation report",
    )
    args = parser.parse_args()

    data_path = Path(args.data_dir)
    print(f"Loading snapshot datasets from {data_path}...")

    def load_split(name: str) -> Optional[pd.DataFrame]:
        for candidate in [
            data_path / f"features_{name}.csv",
            data_path / f"{name}.csv",
            Path("data/features") / f"features_{name}.csv",
        ]:
            if candidate.exists():
                return pd.read_csv(candidate)
        return None

    df_test = load_split("test")
    if df_test is None:
        df_test = load_split("train")

    if df_test is None:
        raise FileNotFoundError("Could not find snapshot dataset for evaluation.")

    print(f"Loaded dataset split with {len(df_test)} snapshots.")

    df_train = load_split("train")
    model = CashFlowForecastModel()
    if df_train is not None:
        print("Fitting CashFlowForecastModel for trajectory predictions...")
        model.fit(df_train)

    calc = SpendableCalculator()
    rec_engine = RecommendationEngine()
    sim = ScenarioSimulator(calc)
    expl_gen = ExplanationGenerator()

    sample_rows = min(50, len(df_test))
    print(f"Generating recommendations & explanations across {sample_rows} snapshots...")

    sample_evaluations = []
    rec_counts = {}

    for idx in range(sample_rows):
        row = df_test.iloc[idx].to_dict()
        user_id = str(row.get("account_id", row.get("user_id", "USER")))
        snapshot_time = str(row.get("snapshot_time", "2026-03-01"))
        current_balance = float(row.get("current_balance", 0.0))

        forecast = model.predict_snapshot(row) if model.is_fitted else None

        sp_out = calc.calculate(
            user_id=user_id,
            snapshot_time=snapshot_time,
            current_balance=current_balance,
            features=row,
            commitments=[],
            forecast=forecast,
        )

        recs = rec_engine.generate_recommendations(sp_out)
        for r in recs:
            rec_counts[r.type.value] = rec_counts.get(r.type.value, 0) + 1

        context = expl_gen.build_context(sp_out, recs)
        explanation = expl_gen.explain(context)

        if idx < 5:
            # Also simulate a scenario for sample inspection
            sc_res = sim.simulate(
                user_id=user_id,
                snapshot_time=snapshot_time,
                current_balance=current_balance,
                features=row,
                commitments=[],
                forecast=forecast,
                scenario_input=ScenarioInput(scenario_type=ScenarioType.ONE_TIME_EXPENSE, amount=5000.0)
            )
            sc_recs = rec_engine.generate_recommendations(sp_out, sc_res)
            sc_context = expl_gen.build_context(sp_out, sc_recs, sc_res)
            sc_expl = expl_gen.explain(sc_context)

            sample_evaluations.append({
                "user_id": user_id,
                "current_balance": sp_out.current_balance,
                "spendable_amount": sp_out.spendable_amount,
                "liquidity_state": sp_out.liquidity_state.value,
                "recommendations_generated": [r.model_dump() for r in recs],
                "explanation_output": explanation.model_dump(),
                "scenario_explanation_output": sc_expl.model_dump(),
            })

    report = {
        "snapshots_evaluated": sample_rows,
        "recommendation_counts_by_type": rec_counts,
        "sample_evaluations": sample_evaluations,
        "summary": "Stage 6 Recommendation + Explanation Engine executed successfully with deterministic fallback support."
    }

    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Successfully saved Stage 6 report at: {output_path}")


if __name__ == "__main__":
    main()
