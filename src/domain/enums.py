from enum import Enum


class BorrowerType(str, Enum):
    STUDENT = "STUDENT"
    POSTGRADUATE = "POSTGRADUATE"
    STAFF = "STAFF"


class LoanStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class EquipmentStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ON_LOAN = "ON_LOAN"
