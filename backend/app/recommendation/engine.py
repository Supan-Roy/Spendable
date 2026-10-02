"""Recommendation Engine Manager.

Executes rule evaluation, deduplication, and priority sorting.
"""

from typing import Dict, List, Optional, Any
from app.engine.schema import SpendableOutput
from app.scenario.schema import ScenarioResult
from app.recommendation.schema import Recommendation, RecommendationPriority
from app.recommendation.rules import RecommendationRulesEvaluator


class RecommendationEngine:
    """Manager class generating prioritized deterministic recommendations."""

    def __init__(self, evaluator: Optional[RecommendationRulesEvaluator] = None):
        self.evaluator = evaluator or RecommendationRulesEvaluator()

    def generate_recommendations(
        self,
        spendable_output: SpendableOutput,
        scenario_result: Optional[ScenarioResult] = None,
    ) -> List[Recommendation]:
        """Generate, deduplicate, and sort recommendations by presentation priority."""
        raw_recs = self.evaluator.evaluate(spendable_output, scenario_result)

        # Priority mapping for sorting: CRITICAL = 0, WARNING = 1, INFO = 2
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.WARNING: 1,
            RecommendationPriority.INFO: 2,
        }

        # Deduplicate by (type, title)
        seen_keys = set()
        unique_recs: List[Recommendation] = []

        for rec in raw_recs:
            key = (rec.type, rec.title)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_recs.append(rec)

        # Sort by priority
        sorted_recs = sorted(unique_recs, key=lambda r: priority_order.get(r.priority, 99))
        return sorted_recs
