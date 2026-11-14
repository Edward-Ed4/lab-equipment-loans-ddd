from src.application.dtos import IssueLoanRequest
from src.application.event_dispatcher import EventDispatcher
from src.application.handlers import LoanIssuedHandler
from src.application.issue_loan_service import IssueLoanService
from src.domain.borrower import Borrower
from src.domain.enums import BorrowerType, EquipmentStatus, LoanStatus
from src.domain.events import LoanIssued
from src.domain.equipment import Equipment
from src.domain.services import BorrowingEligibilityService
from src.infrastructure.in_memory_repositories import (
    InMemoryBorrowerRepository,
    InMemoryEquipmentRepository,
)


def test_T7_main_use_case_success():
    # T7: full issue-loan flow succeeds, updates borrower and equipment, and handles the event.
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower = Borrower("b-21", "Ava", BorrowerType.STAFF)
    equipment = Equipment("eq-21", "Projector")
    borrower_repo.save(borrower)
    equipment_repo.save(equipment)

    dispatcher = EventDispatcher()
    dispatcher.register(LoanIssued, LoanIssuedHandler(equipment_repo))
    service = IssueLoanService(
        borrower_repo,
        equipment_repo,
        BorrowingEligibilityService(),
        dispatcher,
    )

    result = service.execute(IssueLoanRequest("b-21", "eq-21", 3))
    assert result.outcome == "ISSUED"
    assert result.loan_id is not None
    assert borrower_repo.get("b-21").active_loan_count() == 1
    assert borrower_repo.get("b-21")._loans[0].status == LoanStatus.ACTIVE
    assert equipment_repo.get("eq-21").status == EquipmentStatus.ON_LOAN


def test_T8_equipment_rejects_follow_up():
    # T8: if equipment is already on loan, the issue fails and the new borrower's loan is cancelled.
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower = Borrower("b-22", "Nina", BorrowerType.STAFF)
    equipment = Equipment("eq-22", "Scanner")
    equipment.status = EquipmentStatus.ON_LOAN
    borrower_repo.save(borrower)
    equipment_repo.save(equipment)

    dispatcher = EventDispatcher()
    dispatcher.register(LoanIssued, LoanIssuedHandler(equipment_repo))
    service = IssueLoanService(
        borrower_repo,
        equipment_repo,
        BorrowingEligibilityService(),
        dispatcher,
    )

    result = service.execute(IssueLoanRequest("b-22", "eq-22", 2))
    assert result.outcome == "EQUIPMENT_UNAVAILABLE"
    assert result.loan_id is not None
    stored_borrower = borrower_repo.get("b-22")
    assert stored_borrower.active_loan_count() == 0
    assert len(stored_borrower._loans) == 1
    assert stored_borrower._loans[0].status == LoanStatus.CANCELLED
    assert equipment_repo.get("eq-22").status == EquipmentStatus.ON_LOAN
