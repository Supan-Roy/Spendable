"""Feature definitions, metadata schemas, and Feature Catalog specifications."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class FeatureCategory(str, Enum):
    """Categorical grouping for financial feature intelligence."""
    LIQUIDITY = "LIQUIDITY"
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"
    CASH_FLOW = "CASH_FLOW"
    SPENDING_BEHAVIOR = "SPENDING_BEHAVIOR"
    BALANCE_PRESSURE = "BALANCE_PRESSURE"


class FeatureDefinition(BaseModel):
    """Metadata specification for an individual engineered feature."""
    name: str
    category: FeatureCategory
    data_type: str  # "float", "int", "bool"
    unit: str  # "BDT", "days", "count", "ratio", "slope"
    time_window: str  # "snapshot", "7d", "14d", "30d"
    description: str
    is_observable: bool = True
    requires_fitting: bool = False
    leakage_risk: str = "LOW"
    intended_downstream_use: str

    model_config = ConfigDict(from_attributes=True)


FEATURE_CATALOG: List[FeatureDefinition] = [
    # A. Liquidity Features
    FeatureDefinition(
        name="current_balance",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="snapshot",
        description="Latest observed account balance at snapshot timestamp T",
        intended_downstream_use="Baseline liquidity anchor for runway calculation",
    ),
    FeatureDefinition(
        name="balance_min_7d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="7d",
        description="Minimum account balance observed in the past 7 days prior to snapshot T",
        intended_downstream_use="Short-term minimum balance buffer tracking",
    ),
    FeatureDefinition(
        name="balance_min_14d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="14d",
        description="Minimum account balance observed in the past 14 days prior to snapshot T",
        intended_downstream_use="Biweekly balance buffer tracking",
    ),
    FeatureDefinition(
        name="balance_min_30d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Minimum account balance observed in the past 30 days prior to snapshot T",
        intended_downstream_use="Monthly minimum balance floor tracking",
    ),
    FeatureDefinition(
        name="balance_max_30d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Maximum account balance observed in the past 30 days prior to snapshot T",
        intended_downstream_use="Peak account liquidity tracking",
    ),
    FeatureDefinition(
        name="balance_mean_30d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Mean account balance across transactions in the past 30 days prior to snapshot T",
        intended_downstream_use="Average rolling liquidity level",
    ),
    FeatureDefinition(
        name="balance_std_30d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Standard deviation of account balance in the past 30 days prior to snapshot T",
        intended_downstream_use="Account balance stability & volatility",
    ),
    FeatureDefinition(
        name="balance_change_7d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="7d",
        description="Absolute change in account balance over the past 7 days (current_balance - balance_7d_ago)",
        intended_downstream_use="Short-term balance trajectory velocity",
    ),
    FeatureDefinition(
        name="balance_change_30d",
        category=FeatureCategory.LIQUIDITY,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Absolute change in account balance over the past 30 days (current_balance - balance_30d_ago)",
        intended_downstream_use="Monthly balance trajectory velocity",
    ),

    # B. Inflow Features
    FeatureDefinition(
        name="total_inflow_7d",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="BDT",
        time_window="7d",
        description="Total monetary inflow sum received in the past 7 days prior to snapshot T",
        intended_downstream_use="Recent 7-day inflow volume",
    ),
    FeatureDefinition(
        name="total_inflow_14d",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="BDT",
        time_window="14d",
        description="Total monetary inflow sum received in the past 14 days prior to snapshot T",
        intended_downstream_use="Biweekly inflow volume",
    ),
    FeatureDefinition(
        name="total_inflow_30d",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Total monetary inflow sum received in the past 30 days prior to snapshot T",
        intended_downstream_use="Monthly inflow capacity",
    ),
    FeatureDefinition(
        name="inflow_count_30d",
        category=FeatureCategory.INFLOW,
        data_type="int",
        unit="count",
        time_window="30d",
        description="Count of inflow transactions in the past 30 days prior to snapshot T",
        intended_downstream_use="Inflow frequency & multi-source income detection",
    ),
    FeatureDefinition(
        name="avg_inflow_amount_30d",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Mean inflow transaction amount in the past 30 days prior to snapshot T",
        intended_downstream_use="Typical incoming transaction size",
    ),
    FeatureDefinition(
        name="days_since_last_inflow",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="days",
        time_window="historical",
        description="Days elapsed between the most recent inflow transaction and snapshot T",
        intended_downstream_use="Paycheck cycle proximity and income recency",
    ),
    FeatureDefinition(
        name="inflow_volatility_30d",
        category=FeatureCategory.INFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Standard deviation of inflow transaction amounts in the past 30 days",
        intended_downstream_use="Income regularity vs freelance variability",
    ),

    # C. Outflow Features
    FeatureDefinition(
        name="total_outflow_7d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="7d",
        description="Total monetary outflow sum spent in the past 7 days prior to snapshot T",
        intended_downstream_use="Recent 7-day spending volume",
    ),
    FeatureDefinition(
        name="total_outflow_14d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="14d",
        description="Total monetary outflow sum spent in the past 14 days prior to snapshot T",
        intended_downstream_use="Biweekly spending volume",
    ),
    FeatureDefinition(
        name="total_outflow_30d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Total monetary outflow sum spent in the past 30 days prior to snapshot T",
        intended_downstream_use="Monthly spending volume",
    ),
    FeatureDefinition(
        name="outflow_count_30d",
        category=FeatureCategory.OUTFLOW,
        data_type="int",
        unit="count",
        time_window="30d",
        description="Count of outflow transactions in the past 30 days prior to snapshot T",
        intended_downstream_use="Monthly transaction activity frequency",
    ),
    FeatureDefinition(
        name="avg_outflow_amount_30d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Mean outflow transaction amount in the past 30 days prior to snapshot T",
        intended_downstream_use="Average transaction ticket size",
    ),
    FeatureDefinition(
        name="median_outflow_amount_30d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Median outflow transaction amount in the past 30 days prior to snapshot T",
        intended_downstream_use="Median spending ticket size robust to outliers",
    ),
    FeatureDefinition(
        name="days_since_last_outflow",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="days",
        time_window="historical",
        description="Days elapsed between the most recent outflow transaction and snapshot T",
        intended_downstream_use="Spending activity recency",
    ),
    FeatureDefinition(
        name="spending_volatility_30d",
        category=FeatureCategory.OUTFLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Standard deviation of outflow transaction amounts in the past 30 days",
        intended_downstream_use="Outflow transaction variability",
    ),

    # D. Cash Flow Features
    FeatureDefinition(
        name="net_cash_flow_7d",
        category=FeatureCategory.CASH_FLOW,
        data_type="float",
        unit="BDT",
        time_window="7d",
        description="Net cash flow (inflow_7d - outflow_7d) in the past 7 days prior to snapshot T",
        intended_downstream_use="Short-term net liquidity accumulation",
    ),
    FeatureDefinition(
        name="net_cash_flow_14d",
        category=FeatureCategory.CASH_FLOW,
        data_type="float",
        unit="BDT",
        time_window="14d",
        description="Net cash flow (inflow_14d - outflow_14d) in the past 14 days prior to snapshot T",
        intended_downstream_use="Biweekly net liquidity accumulation",
    ),
    FeatureDefinition(
        name="net_cash_flow_30d",
        category=FeatureCategory.CASH_FLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Net cash flow (inflow_30d - outflow_30d) in the past 30 days prior to snapshot T",
        intended_downstream_use="Monthly net liquidity accumulation",
    ),
    FeatureDefinition(
        name="inflow_outflow_ratio_30d",
        category=FeatureCategory.CASH_FLOW,
        data_type="float",
        unit="ratio",
        time_window="30d",
        description="Ratio of total inflow to total outflow (inflow_30d / (outflow_30d + 1e-5))",
        intended_downstream_use="Savings multiplier and financial coverage ratio",
    ),
    FeatureDefinition(
        name="avg_daily_net_flow_30d",
        category=FeatureCategory.CASH_FLOW,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Average net cash flow per day over the past 30 days (net_cash_flow_30d / 30.0)",
        intended_downstream_use="Daily burn rate / accumulation rate",
    ),

    # E. Spending Behavior & Concentration
    FeatureDefinition(
        name="avg_transaction_amount_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Mean of all transaction amounts (inflows and outflows) in the past 30 days",
        intended_downstream_use="Overall account transaction intensity",
    ),
    FeatureDefinition(
        name="median_transaction_amount_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="BDT",
        time_window="30d",
        description="Median of all transaction amounts in the past 30 days",
        intended_downstream_use="Overall account median ticket size",
    ),
    FeatureDefinition(
        name="transaction_frequency_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="count/day",
        time_window="30d",
        description="Average daily transaction frequency (total_txns_30d / 30.0)",
        intended_downstream_use="Overall account activity velocity",
    ),
    FeatureDefinition(
        name="essential_spending_share_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="ratio",
        time_window="30d",
        description="Fraction of 30d outflows spent on HOUSING, UTILITIES, and TELECOM categories",
        intended_downstream_use="Fixed / non-discretionary obligation commitment ratio",
    ),
    FeatureDefinition(
        name="discretionary_spending_share_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="ratio",
        time_window="30d",
        description="Fraction of 30d outflows spent on DINING, GROCERIES, DISCRETIONARY_SHOPPING, and ENTERTAINMENT",
        intended_downstream_use="Flexible discretionary spending share",
    ),
    FeatureDefinition(
        name="category_concentration_index_30d",
        category=FeatureCategory.SPENDING_BEHAVIOR,
        data_type="float",
        unit="index",
        time_window="30d",
        description="Herfindahl-Hirschman Index (sum of squared category shares) of 30d outflows",
        intended_downstream_use="Spending category diversification vs concentration",
    ),

    # F. Balance Pressure
    FeatureDefinition(
        name="low_balance_days_ratio_30d",
        category=FeatureCategory.BALANCE_PRESSURE,
        data_type="float",
        unit="ratio",
        time_window="30d",
        description="Fraction of transactions in past 30d where recorded balance_after < ৳1,000.00 BDT",
        intended_downstream_use="Liquidity stress exposure indicator",
    ),
    FeatureDefinition(
        name="drawdown_from_recent_max_30d",
        category=FeatureCategory.BALANCE_PRESSURE,
        data_type="float",
        unit="ratio",
        time_window="30d",
        description="Proportional drawdown of current balance from 30d maximum ((balance_max_30d - current_balance) / balance_max_30d)",
        intended_downstream_use="Peak-to-current account balance depletion",
    ),
    FeatureDefinition(
        name="recent_balance_trend_slope",
        category=FeatureCategory.BALANCE_PRESSURE,
        data_type="float",
        unit="slope",
        time_window="30d",
        description="Linear regression slope of balance_after values over day offsets in 30d window",
        intended_downstream_use="Balance trajectory direction and slope indicator",
    ),
]
