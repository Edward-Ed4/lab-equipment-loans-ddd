import pytest

from src.domain.borrower import Borrower
from src.domain.enums import BorrowerType, EquipmentStatus, LoanStatus
from src.domain.equipment import Equipment
from src.domain.errors import (
    EquipmentUnavailable,
    InvalidLoanPeriod,
    InvalidLoanTransition,
    LoanLimitExceeded,
    NotEligible,
)
from src.domain.loan import Loan
from src.domain.services import BorrowingEligibilityService
from src.domain.value_objects import LoanPeriod


def test_T1_BR1_loan_period():
    # T1: LoanPeriod accepts valid boundaries and rejects invalid values.
    assert LoanPeriod(1).days == 1
    assert LoanPeriod(7).days == 7

    for bad_days in (0, 8):
        with pytest.raises(InvalidLoanPeriod):
            LoanPeriod(bad_days)


def test_T2_BR2_loan_state():
    # T2: Loan activation is valid only from PENDING and cancelled loans cannot reactivate.
    loan = Loan("loan-1", "eq-1", LoanPeriod(3))
    loan.activate()
    assert loan.status == LoanStatus.ACTIVE

    loan.cancel()
    assert loan.status == LoanStatus.CANCELLED

    with pytest.raises(InvalidLoanTransition):
        loan.activate()


def test_T3_BR3_loan_limit():
    # T3: a borrower can issue at most three pending or active loans.
    borrower = Borrower("b-1", "Ava", BorrowerType.STUDENT)

    for index in range(3):
        borrower.issue_loan(f"loan-{index}", f"eq-{index}", LoanPeriod(1))

    assert borrower.active_loan_count() == 3

    with pytest.raises(LoanLimitExceeded):
        borrower.issue_loan("loan-4", "eq-4", LoanPeriod(2))


def test_T4_BR4_eligibility():
    # T4: restricted equipment is only eligible for STAFF or POSTGRADUATE borrowers.
    eligibility_service = BorrowingEligibilityService()
    student = Borrower("b-2", "Ben", BorrowerType.STUDENT)
    staff = Borrower("b-3", "Cara", BorrowerType.STAFF)
    restricted_equipment = Equipment("eq-10", "Laser cutter", restricted=True)

    with pytest.raises(NotEligible):
        eligibility_service.check(student, restricted_equipment)

    eligibility_service.check(staff, restricted_equipment)


def test_T5_BR5_equipment_follow_up():
    # T5: equipment marks on loan only when available and rejects repeated loaning.
    equipment = Equipment("eq-11", "Microscope")
    equipment.mark_on_loan()
    assert equipment.status == EquipmentStatus.ON_LOAN

    with pytest.raises(EquipmentUnavailable):
        equipment.mark_on_loan()


def test_T6_BR6_lookup():
    # T6: missing borrower or equipment returns NOT_FOUND and leaves the repositories unchanged.
    borrower_repo = {}
    equipment_repo = {}

    from src.application.dtos import IssueLoanRequest
    from src.application.event_dispatcher import EventDispatcher
    from src.application.issue_loan_service import IssueLoanService
    from src.domain.services import BorrowingEligibilityService
    from src.infrastructure.in_memory_repositories import (
        InMemoryBorrowerRepository,
        InMemoryEquipmentRepository,
    )

    borrower_store = InMemoryBorrowerRepository()
    equipment_store = InMemoryEquipmentRepository()
    service = IssueLoanService(
        borrower_store,
        equipment_store,
        BorrowingEligibilityService(),
        EventDispatcher(),
    )

    missing_borrower = service.execute(IssueLoanRequest("missing-borrower", "eq-20", 3))
    assert missing_borrower.outcome == "NOT_FOUND"
    assert borrower_store.get("missing-borrower") is None
    assert equipment_store.get("eq-20") is None

    borrower = Borrower("b-9", "Dana", BorrowerType.STAFF)
    borrower_store.save(borrower)
    missing_equipment = service.execute(IssueLoanRequest("b-9", "missing-equipment", 3))
    assert missing_equipment.outcome == "NOT_FOUND"
    assert borrower_store.get("b-9") == borrower
    assert equipment_store.get("missing-equipment") is None
