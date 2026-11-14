from dataclasses import dataclass


@dataclass
class IssueLoanRequest:
    """BR6: request payload for issuing a loan."""

    borrower_id: str
    equipment_id: str
    days: int


@dataclass
class IssueLoanResult:
    """BR6: outcome for an issue-loan request."""

    outcome: str
    loan_id: str | None = None
    message: str = ""
