"""Persona definitions and behavioral profile configurations for synthetic data generation.

Each persona defines starting financial parameters, recurring commitment templates,
discretionary spending tendencies, and behavioral phase transition logic.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
import random
from typing import List, Tuple, Dict, Any, Optional

from app.domain.enums import ActivityType, TransactionDirection
from app.synthetic.enums import PersonaType, RecurrenceFrequency, MilestoneType
from app.synthetic.ground_truth import PlantedRuleGroundTruth, BehaviorMilestoneGroundTruth


class BasePersona(ABC):
    """Base abstract class for synthetic user behavioral personas."""

    def __init__(self, persona_type: PersonaType, rng: random.Random):
        self.persona_type = persona_type
        self.rng = rng

    @abstractmethod
    def get_starting_balance(self) -> Decimal:
        """Generate initial account balance."""
        pass

    @abstractmethod
    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        """Generate planted recurring commitment rules for ground truth."""
        pass

    @abstractmethod
    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        """Generate behavioral milestone events (e.g. drift start date)."""
        pass

    @abstractmethod
    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Evaluate and return raw activity candidates for the current simulation day.
        
        Returns a tuple of (activity_candidates, active_phase_label).
        """
        pass


class StablePersona(BasePersona):
    """Stable financial behavior: regular income, predictable expenses, healthy liquidity."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.STABLE, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(60000, 150000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        salary_amount = Decimal(str(self.rng.randint(70000, 120000)))
        rent_amount = Decimal(str(self.rng.randint(18000, 30000)))
        internet_amount = Decimal(str(self.rng.randint(1200, 2500)))
        mobile_amount = Decimal(str(self.rng.randint(500, 1200)))
        utility_amount = Decimal(str(self.rng.randint(3000, 6000)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Tech Global Corp Payroll",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=1,
                base_amount=salary_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="Property Management Ltd",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=5,
                base_amount=rent_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="Link3 Broadband",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=10,
                base_amount=internet_amount,
                amount_variance_pct=0.02,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_mobile_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MOBILE_RECHARGE,
                category="TELECOM",
                counterparty_name="Grameenphone Airtime",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=15,
                base_amount=mobile_amount,
                amount_variance_pct=0.05,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_utility_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="DPDC Electricity",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=20,
                base_amount=utility_amount,
                amount_variance_pct=0.10,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        return []

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        phase = "STABLE_NORMAL"

        # Check planted recurring rules
        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                var_multiplier = 1.0 + self.rng.uniform(-rule.amount_variance_pct, rule.amount_variance_pct)
                amt = (rule.base_amount * Decimal(str(round(var_multiplier, 4)))).quantize(Decimal("0.01"))
                direction = TransactionDirection.INFLOW if rule.activity_type == ActivityType.SALARY else TransactionDirection.OUTFLOW
                candidates.append({
                    "direction": direction,
                    "activity_type": rule.activity_type,
                    "amount": amt,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "ONLINE_BANKING" if direction == TransactionDirection.INFLOW else "DIGITAL_PAYMENT",
                    "planted_rule_id": rule.rule_id,
                })

        # Daily discretionary activities
        # Groceries / Food (~3 times a week)
        if self.rng.random() < 0.45:
            amt = Decimal(str(self.rng.randint(400, 2500)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "FOOD_AND_GROCERIES",
                "counterparty_name": self.rng.choice(["Shwapno Superstore", "Meena Bazar", "Local Market", "Sultan's Dine"]),
                "channel": "POS_TERMINAL",
                "planted_rule_id": None,
            })

        # Transportation / Commute
        if current_date.weekday() < 5 and self.rng.random() < 0.6:
            amt = Decimal(str(self.rng.randint(150, 600)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "TRANSPORT",
                "counterparty_name": self.rng.choice(["Pathao Ride", "Uber India/BD", "Metro Rail Card"]),
                "channel": "MOBILE_APP",
                "planted_rule_id": None,
            })

        return candidates, phase


class TightLiquidityPersona(BasePersona):
    """Tight liquidity: modest income, heavy recurring obligations, small remaining buffer."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.TIGHT_LIQUIDITY, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(4000, 12000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        salary_amount = Decimal(str(self.rng.randint(28000, 38000)))
        rent_amount = Decimal(str(self.rng.randint(14000, 20000)))
        utility_amount = Decimal(str(self.rng.randint(2000, 3500)))
        mobile_amount = Decimal(str(self.rng.randint(400, 800)))
        internet_amount = Decimal(str(self.rng.randint(800, 1500)))
        family_amount = Decimal(str(self.rng.randint(4000, 7000)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Local Enterprise Payroll",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=1,
                base_amount=salary_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="House Owner Direct",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=3,
                base_amount=rent_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_family_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.P2P_TRANSFER,
                category="FAMILY_SUPPORT",
                counterparty_name="Family Member Account",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=6,
                base_amount=family_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="Carnival Broadband",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=10,
                base_amount=internet_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_mobile_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MOBILE_RECHARGE,
                category="TELECOM",
                counterparty_name="Robi Airtime",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=14,
                base_amount=mobile_amount,
                amount_variance_pct=0.05,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_utility_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="DESCO Electricity",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=18,
                base_amount=utility_amount,
                amount_variance_pct=0.10,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        return []

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        phase = "TIGHT_NORMAL"

        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                var_multiplier = 1.0 + self.rng.uniform(-rule.amount_variance_pct, rule.amount_variance_pct)
                amt = (rule.base_amount * Decimal(str(round(var_multiplier, 4)))).quantize(Decimal("0.01"))
                direction = TransactionDirection.INFLOW if rule.activity_type == ActivityType.SALARY else TransactionDirection.OUTFLOW
                candidates.append({
                    "direction": direction,
                    "activity_type": rule.activity_type,
                    "amount": amt,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "MOBILE_BANKING",
                    "planted_rule_id": rule.rule_id,
                })

        # Discretionary spending adaptively capped if balance gets low
        if current_balance > Decimal("2000.00") and self.rng.random() < 0.5:
            amt = Decimal(str(self.rng.randint(150, 800)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "FOOD_AND_DINING",
                "counterparty_name": self.rng.choice(["Local Tea Stall", "Corner Grocery", "Foodpanda BD", "Tong Tea"]),
                "channel": "AGENT_QR",
                "planted_rule_id": None,
            })

        return candidates, phase


class IrregularIncomePersona(BasePersona):
    """Irregular income: variable/irregular inflows, variable expenses."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.IRREGULAR_INCOME, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(20000, 50000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        rent_amount = Decimal(str(self.rng.randint(15000, 22000)))
        internet_amount = Decimal(str(self.rng.randint(1000, 2000)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="Studio Rent Payment",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=5,
                base_amount=rent_amount,
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="AmberIT Fiber",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=12,
                base_amount=internet_amount,
                amount_variance_pct=0.0,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        return []

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        phase = "IRREGULAR_NORMAL"

        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                candidates.append({
                    "direction": TransactionDirection.OUTFLOW,
                    "activity_type": rule.activity_type,
                    "amount": rule.base_amount,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "MOBILE_BANKING",
                    "planted_rule_id": rule.rule_id,
                })

        # Irregular freelance / contract payouts (~every 10 to 22 days probabilistically)
        if self.rng.random() < 0.08:
            income_amt = Decimal(str(self.rng.randint(15000, 65000)))
            candidates.append({
                "direction": TransactionDirection.INFLOW,
                "activity_type": self.rng.choice([ActivityType.P2P_TRANSFER, ActivityType.CASH_IN, ActivityType.OTHER]),
                "amount": income_amt,
                "category": "FREELANCE_INCOME",
                "counterparty_name": self.rng.choice(["Upwork Escrow", "Fiverr Inc", "Client Direct Transfer", "Design Studio Payout"]),
                "channel": "BANK_TRANSFER",
                "planted_rule_id": None,
            })

        # Variable discretionary spending
        if self.rng.random() < 0.4:
            amt = Decimal(str(self.rng.randint(300, 3000)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "GENERAL_PURCHASE",
                "counterparty_name": self.rng.choice(["Daraz BD", "Star Tech Hardware", "Coffee World", "Aarong Store"]),
                "channel": "ONLINE_GATEWAY",
                "planted_rule_id": None,
            })

        return candidates, phase


class CommitmentHeavyPersona(BasePersona):
    """Subscription/commitment-heavy: multiple recurring bills/subscriptions across frequencies."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.COMMITMENT_HEAVY, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(50000, 110000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Enterprise Payroll Services",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=1,
                base_amount=Decimal(str(self.rng.randint(90000, 140000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="Luxury Apartments Co",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=2,
                base_amount=Decimal(str(self.rng.randint(25000, 40000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_loan_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.OTHER,
                category="DEBT_PAYMENT",
                counterparty_name="BRAC Bank Personal Loan",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=7,
                base_amount=Decimal(str(self.rng.randint(8000, 18000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="Dotlines Fiber Internet",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=10,
                base_amount=Decimal(str(self.rng.randint(2000, 3500))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_netflix_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MERCHANT_PAYMENT,
                category="ENTERTAINMENT",
                counterparty_name="Netflix Streaming Subscription",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=12,
                base_amount=Decimal("1499.00"),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_spotify_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MERCHANT_PAYMENT,
                category="ENTERTAINMENT",
                counterparty_name="Spotify Music Premium",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=14,
                base_amount=Decimal("399.00"),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_cloud_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MERCHANT_PAYMENT,
                category="SOFTWARE",
                counterparty_name="Google One & Cloud Services",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=18,
                base_amount=Decimal("850.00"),
                amount_variance_pct=0.05,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_gym_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MERCHANT_PAYMENT,
                category="FITNESS",
                counterparty_name="Fitness Plus Gym Membership",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=22,
                base_amount=Decimal("3500.00"),
                amount_variance_pct=0.0,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        return []

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        phase = "COMMITMENT_HEAVY_NORMAL"

        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                var_multiplier = 1.0 + self.rng.uniform(-rule.amount_variance_pct, rule.amount_variance_pct)
                amt = (rule.base_amount * Decimal(str(round(var_multiplier, 4)))).quantize(Decimal("0.01"))
                direction = TransactionDirection.INFLOW if rule.activity_type == ActivityType.SALARY else TransactionDirection.OUTFLOW
                candidates.append({
                    "direction": direction,
                    "activity_type": rule.activity_type,
                    "amount": amt,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "CARD_AUTOPAY" if direction == TransactionDirection.OUTFLOW else "BANK_TRANSFER",
                    "planted_rule_id": rule.rule_id,
                })

        # Controlled discretionary
        if self.rng.random() < 0.35:
            amt = Decimal(str(self.rng.randint(500, 2000)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "DINING",
                "counterparty_name": self.rng.choice(["Nando's BD", "Starbucks BD", "Chillox Burgers"]),
                "channel": "CREDIT_CARD",
                "planted_rule_id": None,
            })

        return candidates, phase


class SpendingDriftPersona(BasePersona):
    """Spending drift: historically stable behavior, gradually increasing discretionary spending."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.SPENDING_DRIFT, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(50000, 90000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Software Corp Salary",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=1,
                base_amount=Decimal(str(self.rng.randint(75000, 95000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="Apartment Rent",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=4,
                base_amount=Decimal(str(self.rng.randint(20000, 28000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name="Link3 Broadband",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=10,
                base_amount=Decimal("1500.00"),
                amount_variance_pct=0.0,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        drift_day_offset = duration_days // 2
        effective_date = start_date + timedelta(days=drift_day_offset)
        return [
            BehaviorMilestoneGroundTruth(
                account_id=account_id,
                milestone_type=MilestoneType.DRIFT_START,
                effective_date=effective_date,
                description="Discretionary spending frequency and average ticket size begin gradual upward drift.",
                params={"drift_multiplier_max": 2.2, "drift_start_day": drift_day_offset},
            )
        ]

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        is_drifting = day_index >= (total_days // 2)
        phase = "SPENDING_DRIFT_ACTIVE" if is_drifting else "STABLE_BASELINE"

        # Check planted rules
        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                direction = TransactionDirection.INFLOW if rule.activity_type == ActivityType.SALARY else TransactionDirection.OUTFLOW
                candidates.append({
                    "direction": direction,
                    "activity_type": rule.activity_type,
                    "amount": rule.base_amount,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "BANK_TRANSFER",
                    "planted_rule_id": rule.rule_id,
                })

        # Discretionary spending logic
        prob = 0.35 if not is_drifting else 0.75
        drift_factor = 1.0 if not is_drifting else (1.0 + (day_index - total_days // 2) / (total_days // 2) * 1.2)

        if self.rng.random() < prob:
            base_amt = self.rng.randint(400, 2000)
            amt = (Decimal(str(base_amt)) * Decimal(str(round(drift_factor, 2)))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "DISCRETIONARY_SHOPPING",
                "counterparty_name": self.rng.choice(["Daraz Premium", "Unimart Gourmet", "Gadget & Gear", "Star Cineplex VIP"]),
                "channel": "CREDIT_CARD",
                "planted_rule_id": None,
            })

        return candidates, phase


class FinancialPressurePersona(BasePersona):
    """Financial pressure: stable income, but commitments surge or liquidity deteriorates."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.FINANCIAL_PRESSURE, rng)

    def get_starting_balance(self) -> Decimal:
        return Decimal(str(self.rng.randint(35000, 60000)))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Corporate Employer Inc",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=1,
                base_amount=Decimal(str(self.rng.randint(55000, 70000))),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="House Rent Owner",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=5,
                base_amount=Decimal(str(self.rng.randint(22000, 28000))),
                amount_variance_pct=0.0,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        pressure_day_offset = duration_days // 3
        effective_date = start_date + timedelta(days=pressure_day_offset)
        return [
            BehaviorMilestoneGroundTruth(
                account_id=account_id,
                milestone_type=MilestoneType.PRESSURE_START,
                effective_date=effective_date,
                description="Medical/Emergency outflow commitments begin accumulating, reducing liquidity buffer.",
                params={"pressure_start_day": pressure_day_offset},
            )
        ]

    def evaluate_daily_activities(
        self,
        account_id: str,
        current_date: datetime,
        day_index: int,
        total_days: int,
        current_balance: Decimal,
        planted_rules: List[PlantedRuleGroundTruth],
    ) -> Tuple[List[Dict[str, Any]], str]:
        candidates = []
        under_pressure = day_index >= (total_days // 3)
        phase = "FINANCIAL_PRESSURE_ACTIVE" if under_pressure else "BASELINE_NORMAL"

        day_of_month = current_date.day
        for rule in planted_rules:
            if rule.frequency == RecurrenceFrequency.MONTHLY and day_of_month == rule.target_day:
                direction = TransactionDirection.INFLOW if rule.activity_type == ActivityType.SALARY else TransactionDirection.OUTFLOW
                candidates.append({
                    "direction": direction,
                    "activity_type": rule.activity_type,
                    "amount": rule.base_amount,
                    "category": rule.category,
                    "counterparty_name": rule.counterparty_name,
                    "channel": "BANK_TRANSFER",
                    "planted_rule_id": rule.rule_id,
                })

        # Under pressure, emergency loan or medical payments occur periodically
        if under_pressure and self.rng.random() < 0.15:
            amt = Decimal(str(self.rng.randint(4000, 12000)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.P2P_TRANSFER,
                "amount": amt,
                "category": "MEDICAL_OR_EMERGENCY",
                "counterparty_name": self.rng.choice(["Square Hospital BD", "Emergency Medical Care", "Family Debt Repayment"]),
                "channel": "MOBILE_BANKING",
                "planted_rule_id": None,
            })
        elif not under_pressure and self.rng.random() < 0.3:
            amt = Decimal(str(self.rng.randint(300, 1200)))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": amt,
                "category": "FOOD_AND_DINING",
                "counterparty_name": "Standard Restaurant",
                "channel": "POS_TERMINAL",
                "planted_rule_id": None,
            })

        return candidates, phase


def create_persona(persona_type: PersonaType, rng: random.Random) -> BasePersona:
    """Factory function instantiating persona implementation."""
    mapping = {
        PersonaType.STABLE: StablePersona,
        PersonaType.TIGHT_LIQUIDITY: TightLiquidityPersona,
        PersonaType.IRREGULAR_INCOME: IrregularIncomePersona,
        PersonaType.COMMITMENT_HEAVY: CommitmentHeavyPersona,
        PersonaType.SPENDING_DRIFT: SpendingDriftPersona,
        PersonaType.FINANCIAL_PRESSURE: FinancialPressurePersona,
    }
    cls = mapping.get(persona_type)
    if not cls:
        raise ValueError(f"Unsupported persona type: {persona_type}")
    return cls(rng)
