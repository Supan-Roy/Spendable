"""Synthetic Financial Data Generator core engine.

Produces realistic temporal financial transaction histories conforming to the
Spendable financial data contract. Operates deterministically based on input seed
and configuration. Maintains separate ground-truth metadata, user-level splits,
and offline evaluation future outcomes.
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
    FutureOutcomeGroundTruth,
)
from app.synthetic.validator import validate_synthetic_dataset


class SyntheticDataGenerator:
    """Deterministic, persona-based synthetic financial data generator."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def _determine_user_split(self, user_idx: int) -> str:
        """Assign user to TRAIN, VALIDATION, or TEST split deterministically."""
        train_cutoff = int(self.config.num_users * self.config.train_split)
        val_cutoff = train_cutoff + int(self.config.num_users * self.config.val_split)
        if user_idx < train_cutoff:
            return "TRAIN"
        elif user_idx < val_cutoff:
            return "VALIDATION"
        else:
            return "TEST"

    def _calculate_future_outcomes(self, user_activities: List[Dict[str, Any]], account_id: str) -> List[FutureOutcomeGroundTruth]:
        """Compute offline evaluation future outcomes at historical checkpoints (days 30, 60, 90...)."""
        if not user_activities:
            return []

        outcomes: List[FutureOutcomeGroundTruth] = []
        user_acts_sorted = sorted(user_activities, key=lambda x: x["timestamp_utc"])

        # Checkpoints every 30 days
        start_ts = user_acts_sorted[0]["timestamp_utc"]
        end_ts = user_acts_sorted[-1]["timestamp_utc"]

        current_chk = start_ts + timedelta(days=30)
        while current_chk + timedelta(days=30) <= end_ts:
            # Find balance at current_chk
            past_acts = [a for a in user_acts_sorted if a["timestamp_utc"] <= current_chk]
            obs_bal = Decimal(str(past_acts[-1]["balance_after"])) if past_acts else Decimal("0.00")

            # Future activities within 7d, 14d, 30d
            f7 = [a for a in user_acts_sorted if current_chk < a["timestamp_utc"] <= current_chk + timedelta(days=7)]
            f14 = [a for a in user_acts_sorted if current_chk < a["timestamp_utc"] <= current_chk + timedelta(days=14)]
            f30 = [a for a in user_acts_sorted if current_chk < a["timestamp_utc"] <= current_chk + timedelta(days=30)]

            b7 = [Decimal(str(a["balance_after"])) for a in f7] if f7 else [obs_bal]
            b14 = [Decimal(str(a["balance_after"])) for a in f14] if f14 else [obs_bal]
            b30 = [Decimal(str(a["balance_after"])) for a in f30] if f30 else [obs_bal]

            in7 = sum((Decimal(str(a["amount"])) for a in f7 if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"), Decimal("0.00"))
            in14 = sum((Decimal(str(a["amount"])) for a in f14 if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"), Decimal("0.00"))
            in30 = sum((Decimal(str(a["amount"])) for a in f30 if str(a["direction"]).replace("TransactionDirection.", "") == "INFLOW"), Decimal("0.00"))

            out7 = sum((Decimal(str(a["amount"])) for a in f7 if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"), Decimal("0.00"))
            out14 = sum((Decimal(str(a["amount"])) for a in f14 if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"), Decimal("0.00"))
            out30 = sum((Decimal(str(a["amount"])) for a in f30 if str(a["direction"]).replace("TransactionDirection.", "") == "OUTFLOW"), Decimal("0.00"))

            min_b30 = min(b30)
            stress = min_b30 < Decimal("1000.00")

            outcomes.append(
                FutureOutcomeGroundTruth(
                    account_id=account_id,
                    checkpoint_date=current_chk,
                    observed_balance=obs_bal,
                    future_min_balance_7d=min(b7),
                    future_min_balance_14d=min(b14),
                    future_min_balance_30d=min_b30,
                    future_inflow_sum_7d=in7,
                    future_inflow_sum_14d=in14,
                    future_inflow_sum_30d=in30,
                    future_outflow_sum_7d=out7,
                    future_outflow_sum_14d=out14,
                    future_outflow_sum_30d=out30,
                    liquidity_stress_event_within_30d=stress,
                )
            )

            current_chk += timedelta(days=30)

        return outcomes

    def generate(self) -> Tuple[List[Dict[str, Any]], DatasetGroundTruth]:
        """Generate a complete synthetic financial dataset.
        
        Returns:
            Tuple of (activities_list, ground_truth_metadata).
        """
        all_activities: List[Dict[str, Any]] = []

        ground_truth = DatasetGroundTruth(
            seed=self.config.seed,
            num_users=self.config.num_users,
            generated_at_utc=datetime.now(timezone.utc),
            user_splits={},
            users={},
            annotations={},
            future_outcomes=[],
        )

        persona_weights = self.config.get_effective_persona_weights()
        persona_types = list(persona_weights.keys())
        weights = [persona_weights[p] for p in persona_types]

        for user_idx in range(self.config.num_users):
            account_id = f"ACC-{user_idx + 1:04d}"
            split_assignment = self._determine_user_split(user_idx)
            ground_truth.user_splits[account_id] = split_assignment

            # Select persona deterministically
            chosen_persona_type: PersonaType = self.rng.choices(persona_types, weights=weights, k=1)[0]
            persona: BasePersona = create_persona(chosen_persona_type, self.rng)

            starting_balance = persona.get_starting_balance()
            planted_rules = persona.get_planted_rules(account_id)
            milestones = persona.get_milestones(account_id, self.config.start_date, self.config.duration_days)

            ground_truth.users[account_id] = UserGroundTruth(
                account_id=account_id,
                persona=chosen_persona_type,
                starting_balance=starting_balance,
                split_assignment=split_assignment,
                planted_rules=planted_rules,
                milestones=milestones,
            )

            # 1. Collect daily activity candidates
            raw_user_candidates: List[Dict[str, Any]] = []

            for day_index in range(self.config.duration_days):
                current_date = self.config.start_date + timedelta(days=day_index)

                candidates, phase_label = persona.evaluate_daily_activities(
                    account_id=account_id,
                    current_date=current_date,
                    day_index=day_index,
                    total_days=self.config.duration_days,
                    current_balance=starting_balance,
                    planted_rules=planted_rules,
                )

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

            # 2. Sort candidate events chronologically
            raw_user_candidates.sort(key=lambda x: x["timestamp_utc"])

            # 3. Process candidate events and update balance_after
            current_balance = starting_balance
            user_activities: List[Dict[str, Any]] = []

            for candidate in raw_user_candidates:
                direction = candidate["direction"]
                amount = candidate["amount"]

                if direction == TransactionDirection.OUTFLOW and current_balance < amount:
                    if current_balance <= Decimal("0.00"):
                        continue
                    amount = current_balance

                if direction == TransactionDirection.INFLOW:
                    balance_after = (current_balance + amount).quantize(Decimal("0.01"))
                else:
                    balance_after = (current_balance - amount).quantize(Decimal("0.01"))

                current_balance = balance_after

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

                ground_truth.annotations[activity_id] = ActivityAnnotationGroundTruth(
                    activity_id=activity_id,
                    account_id=account_id,
                    persona=chosen_persona_type,
                    planted_rule_id=candidate.get("planted_rule_id"),
                    is_planted_recurring=(candidate.get("planted_rule_id") is not None),
                    persona_phase=candidate["phase_label"],
                )

            # 4. Calculate future evaluation outcomes for ground truth
            future_outcomes = self._calculate_future_outcomes(user_activities, account_id)
            ground_truth.future_outcomes.extend(future_outcomes)

            all_activities.extend(user_activities)

        all_activities.sort(key=lambda x: x["timestamp_utc"])

        # Validate generated dataset
        validate_synthetic_dataset(all_activities, ground_truth)

        return all_activities, ground_truth
