from src.domain.enums import BorrowerType
from src.domain.errors import NotEligible


class BorrowingEligibilityService:
    """BR4: checks whether a borrower can borrow restricted equipment."""

    def check(self, borrower, equipment):
        if equipment.restricted and borrower.borrower_type == BorrowerType.STUDENT:
            raise NotEligible("Restricted equipment can only be borrowed by STAFF or POSTGRADUATE borrowers.")
        return True
