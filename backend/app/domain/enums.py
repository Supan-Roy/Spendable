"""Financial Domain Enums and Core Specifications."""
from enum import Enum


class TransactionDirection(str, Enum):
    """Direction of money movement relative to the observed account."""
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"


class ActivityType(str, Enum):
    """Categorical classification of observed financial activity."""
    MERCHANT_PAYMENT = "MERCHANT_PAYMENT"
    UTILITY_BILL = "UTILITY_BILL"
    MOBILE_RECHARGE = "MOBILE_RECHARGE"
    P2P_TRANSFER = "P2P_TRANSFER"
    CASH_OUT = "CASH_OUT"
    CASH_IN = "CASH_IN"
    SALARY = "SALARY"
    FEE = "FEE"
    OTHER = "OTHER"


class DataProvenance(str, Enum):
    """Origin/provenance of the financial activity record."""
    SYNTHETIC = "SYNTHETIC"
    IMPORTED = "IMPORTED"
    USER_PROVIDED = "USER_PROVIDED"
    CSV_IMPORT = "CSV_IMPORT"
    MFS_WEBHOOK = "MFS_WEBHOOK"
