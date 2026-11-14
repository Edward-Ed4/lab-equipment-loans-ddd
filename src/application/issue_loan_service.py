from uuid import uuid4

from src.domain.errors import (
    InvalidLoanPeriod,
    LoanLimitExceeded,
    NotEligible,
)
from src.domain.value_objects import LoanPeriod
from src.application.dtos import IssueLoanResult


class IssueLoanService:
    """BR6: coordinates all steps for issuing a loan."""

    def __init__(self, borrower_repo, equipment_repo, eligibility_service, dispatcher):
        self.borrower_repo = borrower_repo
        self.equipment_repo = equipment_repo
        self.eligibility_service = eligibility_service
        self.dispatcher = dispatcher

    def execute(self, request):
        try:
            period = LoanPeriod(request.days)
        except InvalidLoanPeriod:
            return IssueLoanResult("INVALID_PERIOD", None, "Loan period must be between 1 and 7 days inclusive.")

        borrower = self.borrower_repo.get(request.borrower_id)
        equipment = self.equipment_repo.get(request.equipment_id)
        if borrower is None or equipment is None:
            return IssueLoanResult("NOT_FOUND", None, "Borrower or equipment does not exist.")

        try:
            self.eligibility_service.check(borrower, equipment)
        except NotEligible:
            return IssueLoanResult("NOT_ELIGIBLE", None, "Borrower is not eligible for this equipment.")

        loan_id = str(uuid4())
        try:
            borrower.issue_loan(loan_id, equipment.equipment_id, period)
        except LoanLimitExceeded:
            return IssueLoanResult("LIMIT_EXCEEDED", None, "Borrower has reached the loan limit.")

        self.borrower_repo.save(borrower)

        events = borrower.pull_events()
        for event in events:
            results = self.dispatcher.publish(event)
            if any(not item.success for item in results):
                borrower.cancel_loan(loan_id)
                self.borrower_repo.save(borrower)
                return IssueLoanResult("EQUIPMENT_UNAVAILABLE", loan_id, "Equipment was not available for loan.")

        return IssueLoanResult("ISSUED", loan_id, "Loan issued successfully.")
