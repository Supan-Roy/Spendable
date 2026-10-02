"""Persona definitions and behavioral profile configurations for synthetic data generation.

Each persona defines starting financial parameters, recurring commitment templates,
discretionary spending tendencies, intra-persona variations, and behavioral phase transition logic.
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
        # User-specific scale factor (0.6 to 2.5) for intra-persona financial diversity
        self.scale_factor = round(self.rng.uniform(0.6, 2.4), 2)
        # User-specific salary day (1 to 5)
        self.salary_day = self.rng.choice([1, 2, 3, 4, 5, 28, 30])

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
        base = self.rng.randint(60000, 150000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        base_salary = Decimal(str(self.rng.randint(60000, 110000))) * Decimal(str(self.scale_factor))
        base_rent = Decimal(str(self.rng.randint(15000, 28000))) * Decimal(str(self.scale_factor))
        base_internet = Decimal(str(self.rng.randint(1000, 2500)))
        base_mobile = Decimal(str(self.rng.randint(400, 1000)))
        base_utility = Decimal(str(self.rng.randint(2500, 5500)))

        employers = ["Tech Global Corp Payroll", "Software Solutions Ltd", "Enterprise Systems Inc", "Apex Brands Payroll", "GlaxoSmithKline BD"]
        properties = ["Property Management Ltd", "Apex Real Estate Holdings", "Green Housing BD", "City View Apartments"]
        internets = ["Link3 Broadband", "Carnival Internet", "AmberIT Fiber", "Dotlines Broadband"]
        mobiles = ["Grameenphone Airtime", "Robi Airtime", "Banglalink Airtime", "Teletalk BD"]
        utilities = ["DPDC Electricity", "DESCO Power", "Dhaka WASA Water", "Titas Gas BD"]

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name=self.rng.choice(employers),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=self.salary_day,
                base_amount=base_salary.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name=self.rng.choice(properties),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=5,
                base_amount=base_rent.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_internet_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name=self.rng.choice(internets),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=10,
                base_amount=base_internet.quantize(Decimal("0.01")),
                amount_variance_pct=0.02,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_mobile_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.MOBILE_RECHARGE,
                category="TELECOM",
                counterparty_name=self.rng.choice(mobiles),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=15,
                base_amount=base_mobile.quantize(Decimal("0.01")),
                amount_variance_pct=0.05,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_utility_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="UTILITIES",
                counterparty_name=self.rng.choice(utilities),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=20,
                base_amount=base_utility.quantize(Decimal("0.01")),
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

        # Discretionary spending (~45% probability)
        if self.rng.random() < 0.45:
            base_amt = self.rng.randint(300, 2200)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("100.00"), amt),
                "category": self.rng.choice(["FOOD_AND_GROCERIES", "DINING", "TRANSPORT", "ENTERTAINMENT"]),
                "counterparty_name": self.rng.choice(["Shwapno Superstore", "Meena Bazar", "Sultan's Dine", "Pathao Ride", "Star Cineplex"]),
                "channel": "POS_TERMINAL",
                "planted_rule_id": None,
            })

        return candidates, phase


class TightLiquidityPersona(BasePersona):
    """Tight liquidity: modest income, heavy recurring commitments, small remaining buffer."""

    def __init__(self, rng: random.Random):
        super().__init__(PersonaType.TIGHT_LIQUIDITY, rng)

    def get_starting_balance(self) -> Decimal:
        base = self.rng.randint(3000, 10000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        salary_amt = Decimal(str(self.rng.randint(25000, 35000))) * Decimal(str(self.scale_factor))
        rent_amt = Decimal(str(self.rng.randint(12000, 18000))) * Decimal(str(self.scale_factor))
        utility_amt = Decimal(str(self.rng.randint(1800, 3200)))
        mobile_amt = Decimal(str(self.rng.randint(350, 750)))
        internet_amt = Decimal(str(self.rng.randint(800, 1400)))
        family_amt = Decimal(str(self.rng.randint(3500, 6500)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name=self.rng.choice(["Local Enterprise Payroll", "Garments Exporters Ltd", "Retail Store Payroll"]),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=self.salary_day,
                base_amount=salary_amt.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="House Owner Rent Direct",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=3,
                base_amount=rent_amt.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_family_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.P2P_TRANSFER,
                category="FAMILY_SUPPORT",
                counterparty_name="Family Member Transfer",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=6,
                base_amount=family_amt.quantize(Decimal("0.01")),
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
                base_amount=internet_amt.quantize(Decimal("0.01")),
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
                base_amount=mobile_amt.quantize(Decimal("0.01")),
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
                base_amount=utility_amt.quantize(Decimal("0.01")),
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

        # Discretionary spending adaptively suppressed if balance is low
        if current_balance > Decimal("1500.00") and self.rng.random() < 0.45:
            base_amt = self.rng.randint(120, 650)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("50.00"), amt),
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
        # Average payout interval (every 10 to 22 days)
        self.payout_interval_days = self.rng.randint(10, 22)

    def get_starting_balance(self) -> Decimal:
        base = self.rng.randint(15000, 45000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        base_rent = Decimal(str(self.rng.randint(12000, 20000))) * Decimal(str(self.scale_factor))
        base_internet = Decimal(str(self.rng.randint(1000, 2000)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_rent_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.UTILITY_BILL,
                category="HOUSING",
                counterparty_name="Studio Rent Direct",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=5,
                base_amount=base_rent.quantize(Decimal("0.01")),
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
                base_amount=base_internet.quantize(Decimal("0.01")),
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

        # Probabilistic freelance payout based on payout_interval_days
        prob = 1.0 / self.payout_interval_days
        if self.rng.random() < prob:
            base_income = self.rng.randint(15000, 55000)
            amt = (Decimal(str(base_income)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.INFLOW,
                "activity_type": self.rng.choice([ActivityType.P2P_TRANSFER, ActivityType.CASH_IN, ActivityType.OTHER]),
                "amount": amt,
                "category": "FREELANCE_INCOME",
                "counterparty_name": self.rng.choice(["Upwork Escrow", "Fiverr Inc", "Client Direct Transfer", "Design Studio Payout"]),
                "channel": "BANK_TRANSFER",
                "planted_rule_id": None,
            })

        # Discretionary spending
        if self.rng.random() < 0.35:
            base_amt = self.rng.randint(300, 2500)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("100.00"), amt),
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
        base = self.rng.randint(45000, 100000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        base_salary = Decimal(str(self.rng.randint(80000, 130000))) * Decimal(str(self.scale_factor))
        base_rent = Decimal(str(self.rng.randint(22000, 36000))) * Decimal(str(self.scale_factor))
        base_loan = Decimal(str(self.rng.randint(7000, 16000)))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Enterprise Payroll Services",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=self.salary_day,
                base_amount=base_salary.quantize(Decimal("0.01")),
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
                base_amount=base_rent.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
            PlantedRuleGroundTruth(
                rule_id=f"rule_loan_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.OTHER,
                category="DEBT_PAYMENT",
                counterparty_name=self.rng.choice(["BRAC Bank Personal Loan", "DBBL Auto Loan", "City Bank EMI"]),
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=7,
                base_amount=base_loan.quantize(Decimal("0.01")),
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
                base_amount=Decimal(str(self.rng.randint(1800, 3200))),
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

        if self.rng.random() < 0.35:
            base_amt = self.rng.randint(400, 1800)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("100.00"), amt),
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
        # Drift start offset (between 30% and 70% of duration)
        self.drift_pct_offset = self.rng.uniform(0.3, 0.7)

    def get_starting_balance(self) -> Decimal:
        base = self.rng.randint(40000, 85000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        base_salary = Decimal(str(self.rng.randint(70000, 95000))) * Decimal(str(self.scale_factor))
        base_rent = Decimal(str(self.rng.randint(18000, 26000))) * Decimal(str(self.scale_factor))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Software Corp Salary",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=self.salary_day,
                base_amount=base_salary.quantize(Decimal("0.01")),
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
                base_amount=base_rent.quantize(Decimal("0.01")),
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
        drift_day_offset = int(duration_days * self.drift_pct_offset)
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
        drift_start_day = int(total_days * self.drift_pct_offset)
        is_drifting = day_index >= drift_start_day
        phase = "SPENDING_DRIFT_ACTIVE" if is_drifting else "STABLE_BASELINE"

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

        prob = 0.35 if not is_drifting else 0.70
        remaining_days = max(1, total_days - drift_start_day)
        drift_factor = 1.0 if not is_drifting else (1.0 + (day_index - drift_start_day) / remaining_days * 1.2)

        if self.rng.random() < prob:
            base_amt = self.rng.randint(400, 1800)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor)) * Decimal(str(round(drift_factor, 2)))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("100.00"), amt),
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
        # Pressure start offset (between 25% and 65% of duration)
        self.pressure_pct_offset = self.rng.uniform(0.25, 0.65)

    def get_starting_balance(self) -> Decimal:
        base = self.rng.randint(30000, 60000)
        return (Decimal(str(base)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))

    def get_planted_rules(self, account_id: str) -> List[PlantedRuleGroundTruth]:
        base_salary = Decimal(str(self.rng.randint(50000, 70000))) * Decimal(str(self.scale_factor))
        base_rent = Decimal(str(self.rng.randint(20000, 28000))) * Decimal(str(self.scale_factor))

        return [
            PlantedRuleGroundTruth(
                rule_id=f"rule_salary_{account_id}",
                account_id=account_id,
                activity_type=ActivityType.SALARY,
                category="INCOME",
                counterparty_name="Corporate Employer Inc",
                frequency=RecurrenceFrequency.MONTHLY,
                target_day=self.salary_day,
                base_amount=base_salary.quantize(Decimal("0.01")),
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
                base_amount=base_rent.quantize(Decimal("0.01")),
                amount_variance_pct=0.0,
            ),
        ]

    def get_milestones(self, account_id: str, start_date: datetime, duration_days: int) -> List[BehaviorMilestoneGroundTruth]:
        pressure_day_offset = int(duration_days * self.pressure_pct_offset)
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
        pressure_start_day = int(total_days * self.pressure_pct_offset)
        under_pressure = day_index >= pressure_start_day
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

        if under_pressure and self.rng.random() < 0.15:
            base_amt = self.rng.randint(3500, 11000)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.P2P_TRANSFER,
                "amount": max(Decimal("500.00"), amt),
                "category": "MEDICAL_OR_EMERGENCY",
                "counterparty_name": self.rng.choice(["Square Hospital BD", "Emergency Medical Care", "Family Debt Repayment"]),
                "channel": "MOBILE_BANKING",
                "planted_rule_id": None,
            })
        elif not under_pressure and self.rng.random() < 0.3:
            base_amt = self.rng.randint(300, 1200)
            amt = (Decimal(str(base_amt)) * Decimal(str(self.scale_factor))).quantize(Decimal("0.01"))
            candidates.append({
                "direction": TransactionDirection.OUTFLOW,
                "activity_type": ActivityType.MERCHANT_PAYMENT,
                "amount": max(Decimal("100.00"), amt),
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
