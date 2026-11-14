from src.application.dtos import IssueLoanRequest
from src.application.event_dispatcher import EventDispatcher
from src.application.handlers import LoanIssuedHandler
from src.application.issue_loan_service import IssueLoanService
from src.domain.borrower import Borrower
from src.domain.enums import BorrowerType, EquipmentStatus, LoanStatus
from src.domain.equipment import Equipment
from src.domain.events import LoanIssued
from src.domain.services import BorrowingEligibilityService
from src.infrastructure.in_memory_repositories import (
    InMemoryBorrowerRepository,
    InMemoryEquipmentRepository,
)


def test_T6_BR6_lookup():
    # T6: unknown borrower and unknown equipment both return NOT_FOUND and leave the existing data unchanged.
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower = Borrower("b-1", "Ava", BorrowerType.STAFF)
    equipment = Equipment("eq-1", "Projector")
    borrower_repo.save(borrower)
    equipment_repo.save(equipment)

    service = IssueLoanService(
        borrower_repo,
        equipment_repo,
        BorrowingEligibilityService(),
        EventDispatcher(),
    )

    missing_borrower = service.execute(IssueLoanRequest("missing-borrower", "eq-1", 3))
    assert missing_borrower.outcome == "NOT_FOUND"
    assert borrower_repo.get("b-1") == borrower
    assert equipment_repo.get("eq-1") == equipment

    missing_equipment = service.execute(IssueLoanRequest("b-1", "missing-equipment", 3))
    assert missing_equipment.outcome == "NOT_FOUND"
    assert borrower_repo.get("b-1") == borrower
    assert equipment_repo.get("eq-1") == equipment


def test_T7_main_use_case_success():
    # T7: the main issue-loan flow succeeds, marks equipment ON_LOAN, and creates exactly one ACTIVE loan.
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower = Borrower("b-2", "Bert", BorrowerType.STAFF)
    equipment = Equipment("eq-2", "Laptop")
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

    result = service.execute(IssueLoanRequest("b-2", "eq-2", 3))
    assert result.outcome == "ISSUED"
    assert result.loan_id is not None
    assert equipment_repo.get("eq-2").status == EquipmentStatus.ON_LOAN

    stored_borrower = borrower_repo.get("b-2")
    assert stored_borrower.active_loan_count() == 1
    assert len(stored_borrower._loans) == 1
    assert stored_borrower._loans[0].status == LoanStatus.ACTIVE
    assert stored_borrower._loans[0].loan_id == result.loan_id


def test_T8_equipment_rejects_follow_up():
    # T8: equipment already ON_LOAN returns EQUIPMENT_UNAVAILABLE, cancels the new loan, and leaves equipment unchanged.
    borrower_repo = InMemoryBorrowerRepository()
    equipment_repo = InMemoryEquipmentRepository()
    borrower = Borrower("b-3", "Cora", BorrowerType.STAFF)
    equipment = Equipment("eq-3", "Microscope")
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

    result = service.execute(IssueLoanRequest("b-3", "eq-3", 2))
    assert result.outcome == "EQUIPMENT_UNAVAILABLE"
    assert result.loan_id is not None

    stored_borrower = borrower_repo.get("b-3")
    assert stored_borrower.active_loan_count() == 0
    assert len(stored_borrower._loans) == 1
    assert stored_borrower._loans[0].status == LoanStatus.CANCELLED
    assert equipment_repo.get("eq-3").status == EquipmentStatus.ON_LOAN
