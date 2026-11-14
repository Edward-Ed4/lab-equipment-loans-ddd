from dataclasses import dataclass

from src.domain.errors import InvalidLoanPeriod


@dataclass(frozen=True)
class LoanPeriod:
    """BR1: no identity - two 3-day periods are interchangeable."""

    days: int

    def __post_init__(self):
        if not 1 <= self.days <= 7:
            raise InvalidLoanPeriod("Loan period must be between 1 and 7 days inclusive.")
