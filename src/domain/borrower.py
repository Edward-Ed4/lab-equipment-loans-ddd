from src.domain.enums import LoanStatus
from src.domain.errors import DomainError, LoanLimitExceeded
from src.domain.events import LoanIssued
from src.domain.loan import Loan


class Borrower:
    """BR3 - invariant: max 3 PENDING/ACTIVE loans"""

    def __init__(self, borrower_id: str, name: str, borrower_type):
        self.borrower_id = borrower_id
        self.name = name
        self.borrower_type = borrower_type
        self._loans = []
        self._events = []

    # Creation has no rules of its own, so a Factory is not justified.
    def issue_loan(self, loan_id: str, equipment_id: str, period) -> Loan:
        if self.active_loan_count() >= 3:
            raise LoanLimitExceeded("A borrower may never hold more than 3 pending or active loans.")

        loan = Loan(loan_id, equipment_id, period)
        loan.activate()
        self._loans.append(loan)
        self._events.append(LoanIssued(loan_id, self.borrower_id, equipment_id))
        return loan

    def cancel_loan(self, loan_id: str):
        loan = self.get_loan(loan_id)
        loan.cancel()

    def pull_events(self):
        events = list(self._events)
        self._events.clear()
        return events

    def get_loan(self, loan_id):
        for loan in self._loans:
            if loan.loan_id == loan_id:
                return loan
        raise DomainError(f"Loan {loan_id} not found for borrower {self.borrower_id}.")

    def active_loan_count(self) -> int:
        return sum(1 for loan in self._loans if loan.status in (LoanStatus.PENDING, LoanStatus.ACTIVE))

    def __eq__(self, other):
        return isinstance(other, Borrower) and self.borrower_id == other.borrower_id

    def __hash__(self):
        return hash(self.borrower_id)
