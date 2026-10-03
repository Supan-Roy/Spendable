"""Spendable Service Orchestration Layer.

Orchestrates calls between data providers and authoritative domain modules:
- Spendable Engine (Stage 4)
- Scenario Simulation Engine (Stage 5)
- Recommendation Engine (Stage 6)
- Gemini Explanation Layer (Stage 6)

Ensures route handlers remain lightweight thin wrappers.
"""

import time
from typing import Dict, List, Optional, Any

from app.services.data_provider import BaseDataProvider, SyntheticDataProvider
from app.engine.calculator import SpendableCalculator
from app.scenario.simulator import ScenarioSimulator
from app.scenario.schema import ScenarioInput, ScenarioResult
from app.recommendation.engine import RecommendationEngine
from app.explanation.gemini import ExplanationGenerator
from app.explanation.schema import GeminiExplanationResponse
from app.schemas.spendable import (
    SpendableOverviewResponse,
    SpendableForecastResponse,
    SpendableActivityListResponse,
    SpendableActivityItem,
    SpendableRecommendationsResponse,
)


class SpendableService:
    """Application orchestration service for Spendable domain operations."""

    def __init__(self, data_provider: Optional[BaseDataProvider] = None):
        from app.services.data_provider import get_data_provider
        self.data_provider = data_provider or get_data_provider()
        self.calculator = SpendableCalculator()
        self.simulator = ScenarioSimulator(self.calculator)
        self.rec_engine = RecommendationEngine()
        self.expl_generator = ExplanationGenerator()

        # High performance in-memory TTL cache (60 seconds)
        self._overview_cache: Dict[str, tuple[float, SpendableOverviewResponse]] = {}
        self._forecast_cache: Dict[str, tuple[float, SpendableForecastResponse]] = {}
        self._recs_cache: Dict[str, tuple[float, SpendableRecommendationsResponse]] = {}
        self._cache_ttl = 60.0  # seconds

    def invalidate_user_cache(self, user_id: Optional[str] = None) -> None:
        """Clear cached calculation state when user data is modified."""
        if user_id:
            clean = str(user_id).strip().lower()
            for cache in (self._overview_cache, self._forecast_cache, self._recs_cache):
                keys = [k for k in cache.keys() if clean in k.lower()]
                for k in keys:
                    cache.pop(k, None)
        else:
            self._overview_cache.clear()
            self._forecast_cache.clear()
            self._recs_cache.clear()

    def _cache_snapshot(self, sp_out) -> None:
        """Persist calculated Spendable snapshot output into database cache."""
        try:
            from app.database import SessionLocal
            from app.models.snapshot import SpendableSnapshot
            session = SessionLocal()
            try:
                existing = (
                    session.query(SpendableSnapshot)
                    .filter(
                        SpendableSnapshot.account_id == sp_out.user_id,
                        SpendableSnapshot.snapshot_time == sp_out.snapshot_time,
                    )
                    .first()
                )
                if not existing:
                    snap_obj = SpendableSnapshot(
                        account_id=sp_out.user_id,
                        snapshot_time=sp_out.snapshot_time,
                        current_balance=sp_out.current_balance,
                        spendable_amount=sp_out.spendable_amount,
                        protected_amount=sp_out.protected_amount,
                        planning_horizon_days=sp_out.planning_horizon_days,
                        expected_inflow=sp_out.expected_inflow,
                        expected_outflow=sp_out.expected_outflow,
                        upcoming_commitments=sp_out.upcoming_commitments,
                        forecasted_minimum_balance=sp_out.forecasted_minimum_balance,
                        safety_reserve=sp_out.safety_reserve,
                        liquidity_state=sp_out.liquidity_state.value if hasattr(sp_out.liquidity_state, "value") else str(sp_out.liquidity_state),
                    )
                    session.add(snap_obj)
                    session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
        except Exception:
            pass

    def get_overview(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> SpendableOverviewResponse:
        """Compute and return main Spendable dashboard overview state with fast TTL caching."""
        cache_key = f"{user_id or 'default'}:{snapshot_time or 'latest'}"
        now = time.time()
        if cache_key in self._overview_cache:
            cached_time, cached_res = self._overview_cache[cache_key]
            if now - cached_time < self._cache_ttl:
                return cached_res

        snap_data = self.data_provider.get_snapshot_data(user_id, snapshot_time)

        sp_out = self.calculator.calculate(
            user_id=snap_data["user_id"],
            snapshot_time=snap_data["snapshot_time"],
            current_balance=snap_data["current_balance"],
            features=snap_data["features"],
            commitments=snap_data["commitments"],
            forecast=snap_data["forecast"],
        )

        # Cache calculated Spendable snapshot
        self._cache_snapshot(sp_out)

        recs = self.rec_engine.generate_recommendations(sp_out)
        context = self.expl_generator.build_context(sp_out, recs)
        explanation = self.expl_generator.explain(context)

        res = SpendableOverviewResponse(
            user_id=sp_out.user_id,
            snapshot_time=sp_out.snapshot_time,
            current_balance=sp_out.current_balance,
            spendable_amount=sp_out.spendable_amount,
            protected_amount=sp_out.protected_amount,
            planning_horizon_days=sp_out.planning_horizon_days,
            liquidity_state=sp_out.liquidity_state,
            expected_inflow=sp_out.expected_inflow,
            expected_outflow=sp_out.expected_outflow,
            upcoming_commitments=sp_out.upcoming_commitments,
            forecasted_minimum_balance=sp_out.forecasted_minimum_balance,
            safety_reserve=sp_out.safety_reserve,
            recommendations=recs,
            factors=sp_out.factors,
            explanation_summary=explanation.summary,
        )

        self._overview_cache[cache_key] = (now, res)
        return res

    def get_forecast(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> SpendableForecastResponse:
        """Return multi-horizon forecasts and daily balance trajectory with TTL caching."""
        cache_key = f"{user_id or 'default'}:{snapshot_time or 'latest'}"
        now = time.time()
        if cache_key in self._forecast_cache:
            cached_time, cached_res = self._forecast_cache[cache_key]
            if now - cached_time < self._cache_ttl:
                return cached_res

        snap_data = self.data_provider.get_snapshot_data(user_id, snapshot_time)
        forecast = snap_data.get("forecast")

        if forecast is None:
            feats = snap_data.get("features", {"current_balance": snap_data.get("current_balance", 0.0), "account_id": user_id})
            forecast = self.data_provider.forecast_model.predict_snapshot(feats)

        sp_out = self.calculator.calculate(
            user_id=snap_data["user_id"],
            snapshot_time=snap_data["snapshot_time"],
            current_balance=snap_data["current_balance"],
            features=snap_data["features"],
            commitments=snap_data["commitments"],
            forecast=snap_data["forecast"],
        )

        effective_safety = sp_out.safety_reserve if sp_out.safety_reserve > 0 else forecast.safety_threshold_bdt

        res = SpendableForecastResponse(
            user_id=forecast.user_id,
            snapshot_time=forecast.snapshot_time,
            current_balance=forecast.current_balance,
            forecast_7d=forecast.forecast_7d,
            forecast_14d=forecast.forecast_14d,
            forecast_30d=forecast.forecast_30d,
            daily_trajectory=forecast.daily_trajectory,
            safety_threshold_bdt=effective_safety,
        )
        self._forecast_cache[cache_key] = (now, res)
        return res

    def get_activities(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> SpendableActivityListResponse:
        """Return recent observed transactions with pagination."""
        raw_res = self.data_provider.get_recent_activities(user_id, limit, offset)

        activity_items = [SpendableActivityItem(**item) for item in raw_res["activities"]]

        return SpendableActivityListResponse(
            total_count=raw_res["total_count"],
            limit=raw_res["limit"],
            offset=raw_res["offset"],
            activities=activity_items,
        )

    def get_recommendations(
        self, user_id: Optional[str] = None, snapshot_time: Optional[str] = None
    ) -> SpendableRecommendationsResponse:
        """Return deterministic recommendations and Gemini explanation with TTL caching."""
        cache_key = f"{user_id or 'default'}:{snapshot_time or 'latest'}"
        now = time.time()
        if cache_key in self._recs_cache:
            cached_time, cached_res = self._recs_cache[cache_key]
            if now - cached_time < self._cache_ttl:
                return cached_res

        snap_data = self.data_provider.get_snapshot_data(user_id, snapshot_time)

        sp_out = self.calculator.calculate(
            user_id=snap_data["user_id"],
            snapshot_time=snap_data["snapshot_time"],
            current_balance=snap_data["current_balance"],
            features=snap_data["features"],
            commitments=snap_data["commitments"],
            forecast=snap_data["forecast"],
        )

        recs = self.rec_engine.generate_recommendations(sp_out)
        context = self.expl_generator.build_context(sp_out, recs)
        explanation = self.expl_generator.explain(context)

        res = SpendableRecommendationsResponse(
            user_id=sp_out.user_id,
            snapshot_time=sp_out.snapshot_time,
            recommendations=recs,
            explanation=explanation,
        )
        self._recs_cache[cache_key] = (now, res)
        return res

    def simulate_scenario(
        self,
        scenario_input: ScenarioInput,
        user_id: Optional[str] = None,
        snapshot_time: Optional[str] = None,
    ) -> ScenarioResult:
        """Simulate a hypothetical scenario without mutating base state."""
        snap_data = self.data_provider.get_snapshot_data(user_id, snapshot_time)

        return self.simulator.simulate(
            user_id=snap_data["user_id"],
            snapshot_time=snap_data["snapshot_time"],
            current_balance=snap_data["current_balance"],
            features=snap_data["features"],
            commitments=snap_data["commitments"],
            forecast=snap_data["forecast"],
            scenario_input=scenario_input,
        )

    def explain(
        self,
        user_id: Optional[str] = None,
        snapshot_time: Optional[str] = None,
        include_scenario: bool = False,
    ) -> GeminiExplanationResponse:
        """Generate human-readable explanation using Gemini API (or fallback)."""
        snap_data = self.data_provider.get_snapshot_data(user_id, snapshot_time)

        sp_out = self.calculator.calculate(
            user_id=snap_data["user_id"],
            snapshot_time=snap_data["snapshot_time"],
            current_balance=snap_data["current_balance"],
            features=snap_data["features"],
            commitments=snap_data["commitments"],
            forecast=snap_data["forecast"],
        )

        sc_res = None
        if include_scenario:
            # Generate default sample scenario for explanation if requested
            sc_res = self.simulator.simulate(
                user_id=snap_data["user_id"],
                snapshot_time=snap_data["snapshot_time"],
                current_balance=snap_data["current_balance"],
                features=snap_data["features"],
                commitments=snap_data["commitments"],
                forecast=snap_data["forecast"],
                scenario_input=None,
            )

        recs = self.rec_engine.generate_recommendations(sp_out, sc_res)
        context = self.expl_generator.build_context(sp_out, recs, sc_res)
        return self.expl_generator.explain(context)
