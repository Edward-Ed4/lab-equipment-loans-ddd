from src.domain.enums import LoanStatus
from src.domain.errors import InvalidLoanTransition


class Loan:
    """BR2 - identity/state rule"""

    def __init__(self, loan_id: str, equipment_id: str, period):
        self.loan_id = loan_id
        self.equipment_id = equipment_id
        self.period = period
        self.status = LoanStatus.PENDING

    def activate(self):
        if self.status != LoanStatus.PENDING:
            raise InvalidLoanTransition("A loan can become ACTIVE only from PENDING.")
        self.status = LoanStatus.ACTIVE

    def cancel(self):
        if self.status == LoanStatus.CANCELLED:
            raise InvalidLoanTransition("A cancelled loan cannot be cancelled again.")
        self.status = LoanStatus.CANCELLED

    def __eq__(self, other):
        return isinstance(other, Loan) and self.loan_id == other.loan_id

    def __hash__(self):
        return hash(self.loan_id)

