"""Synthetic Financial Data Generator core engine.

Produces realistic temporal financial transaction histories conforming to the
Spendable financial data contract. Operates deterministically based on input seed
and configuration. Maintains separate ground-truth metadata.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
import random
import uuid
from typing import List, Dict, Any, Tuple

from app.domain.enums import TransactionDirection, DataProvenance
from app.synthetic.config import GeneratorConfig
from app.synthetic.enums import PersonaType
from app.synthetic.personas import create_persona, BasePersona
from app.synthetic.ground_truth import (
    DatasetGroundTruth,
    UserGroundTruth,
    ActivityAnnotationGroundTruth,
)
from app.synthetic.validator import validate_synthetic_dataset


class SyntheticDataGenerator:
    """Deterministic, persona-based synthetic financial data generator."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def generate(self) -> Tuple[List[Dict[str, Any]], DatasetGroundTruth]:
        """Generate a complete synthetic financial dataset.
        
        Returns:
            Tuple of (activities_list, ground_truth_metadata).
        """
        all_activities: List[Dict[str, Any]] = []

        # Prepare top-level ground truth container
        ground_truth = DatasetGroundTruth(
            seed=self.config.seed,
            num_users=self.config.num_users,
            generated_at_utc=datetime.now(timezone.utc),
            users={},
            annotations={},
        )

        persona_weights = self.config.get_effective_persona_weights()
        persona_types = list(persona_weights.keys())
        weights = [persona_weights[p] for p in persona_types]

        for user_idx in range(self.config.num_users):
            account_id = f"ACC-{user_idx + 1:04d}"

            # Deterministically select persona for user
            chosen_persona_type: PersonaType = self.rng.choices(persona_types, weights=weights, k=1)[0]
            persona: BasePersona = create_persona(chosen_persona_type, self.rng)

            starting_balance = persona.get_starting_balance()
            planted_rules = persona.get_planted_rules(account_id)
            milestones = persona.get_milestones(account_id, self.config.start_date, self.config.duration_days)

            # Record user ground truth metadata
            ground_truth.users[account_id] = UserGroundTruth(
                account_id=account_id,
                persona=chosen_persona_type,
                starting_balance=starting_balance,
                planted_rules=planted_rules,
                milestones=milestones,
            )

            # 1. Collect all raw daily activity candidates for the simulation period
            raw_user_candidates: List[Dict[str, Any]] = []

            for day_index in range(self.config.duration_days):
                current_date = self.config.start_date + timedelta(days=day_index)

                candidates, phase_label = persona.evaluate_daily_activities(
                    account_id=account_id,
                    current_date=current_date,
                    day_index=day_index,
                    total_days=self.config.duration_days,
                    current_balance=starting_balance,  # indicative
                    planted_rules=planted_rules,
                )

                # Assign timestamp to each candidate on current_date
                base_hour = 8
                for i, candidate in enumerate(candidates):
                    hour = min(22, base_hour + i * 2 + self.rng.randint(0, 1))
                    minute = self.rng.randint(0, 59)
                    second = self.rng.randint(0, 59)

                    candidate_copy = dict(candidate)
                    candidate_copy["timestamp_utc"] = current_date.replace(
                        hour=hour,
                        minute=minute,
                        second=second,
                        tzinfo=timezone.utc,
                    )
                    candidate_copy["phase_label"] = phase_label
                    raw_user_candidates.append(candidate_copy)

            # 2. Sort all user candidate events strictly chronologically
            raw_user_candidates.sort(key=lambda x: x["timestamp_utc"])

            # 3. Process candidate events in exact chronological sequence and maintain consistent balance_after
            current_balance = starting_balance
            user_activities: List[Dict[str, Any]] = []

            for candidate in raw_user_candidates:
                direction = candidate["direction"]
                amount = candidate["amount"]

                # Balance protection invariant: prevent impossible negative balance sequence
                if direction == TransactionDirection.OUTFLOW and current_balance < amount:
                    if current_balance <= Decimal("0.00"):
                        # Skip discretionary outflow if balance is exhausted
                        continue
                    # Cap spending to exact available balance
                    amount = current_balance

                if direction == TransactionDirection.INFLOW:
                    balance_after = (current_balance + amount).quantize(Decimal("0.01"))
                else:
                    balance_after = (current_balance - amount).quantize(Decimal("0.01"))

                current_balance = balance_after

                # Deterministic UUID generation
                activity_id = str(uuid.UUID(int=self.rng.getrandbits(128), version=4))

                activity_record = {
                    "id": activity_id,
                    "account_id": account_id,
                    "amount": amount,
                    "currency": self.config.currency,
                    "direction": direction,
                    "activity_type": candidate["activity_type"],
                    "timestamp_utc": candidate["timestamp_utc"],
                    "category": candidate.get("category"),
                    "channel": candidate.get("channel"),
                    "counterparty_name": candidate.get("counterparty_name"),
                    "reference_id": f"TXN-{self.rng.randint(10000000, 99999999)}",
                    "balance_after": balance_after,
                    "provenance": DataProvenance.SYNTHETIC,
                }

                user_activities.append(activity_record)

                # Record ground truth annotation separately
                ground_truth.annotations[activity_id] = ActivityAnnotationGroundTruth(
                    activity_id=activity_id,
                    account_id=account_id,
                    persona=chosen_persona_type,
                    planted_rule_id=candidate.get("planted_rule_id"),
                    is_planted_recurring=(candidate.get("planted_rule_id") is not None),
                    persona_phase=candidate["phase_label"],
                )

            all_activities.extend(user_activities)

        # Sort entire dataset chronologically
        all_activities.sort(key=lambda x: x["timestamp_utc"])

        # Validate dataset against data contract & invariants
        validate_synthetic_dataset(all_activities, ground_truth)

        return all_activities, ground_truth
