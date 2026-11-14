from src.application.dtos import IssueLoanRequest
from src.application.event_dispatcher import EventDispatcher
from src.application.handlers import LoanIssuedHandler
from src.application.issue_loan_service import IssueLoanService
from src.domain.borrower import Borrower
from src.domain.enums import BorrowerType
from src.domain.equipment import Equipment
from src.domain.events import LoanIssued
from src.domain.services import BorrowingEligibilityService
from src.infrastructure.in_memory_repositories import (
    InMemoryBorrowerRepository,
    InMemoryEquipmentRepository,
)


def main():
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower_repo.save(Borrower("b-staff", "Avery", BorrowerType.STAFF))
    equipment_repo.save(Equipment("e-lab", "3D Printer", restricted=False))
    dispatcher = EventDispatcher()
    dispatcher.register(LoanIssued, LoanIssuedHandler(equipment_repo))
    service = IssueLoanService(
        borrower_repo,
        equipment_repo,
        BorrowingEligibilityService(),
        dispatcher,
    )
    result = service.execute(IssueLoanRequest("b-staff", "e-lab", 3))
    print(result)


if __name__ == "__main__":
    main()
