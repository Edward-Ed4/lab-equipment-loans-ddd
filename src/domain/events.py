from dataclasses import dataclass


@dataclass(frozen=True)
class LoanIssued:
    """BR5: event emitted when a loan is issued."""

    loan_id: str
    borrower_id: str
    equipment_id: str
