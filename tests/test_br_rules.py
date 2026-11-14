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
    # T2: PENDING->ACTIVE works; a CANCELLED loan cannot be activated.
    loan = Loan("loan-1", "eq-1", LoanPeriod(3))
    loan.activate()
    assert loan.status == LoanStatus.ACTIVE

    loan.cancel()
    assert loan.status == LoanStatus.CANCELLED

    with pytest.raises(InvalidLoanTransition):
        loan.activate()


def test_T3_BR3_loan_limit():
    # T3: after 3 issued loans the 4th raises LoanLimitExceeded and the borrower still has exactly 3 loans.
    borrower = Borrower("b-1", "Ava", BorrowerType.STUDENT)

    for index in range(3):
        borrower.issue_loan(f"loan-{index}", f"eq-{index}", LoanPeriod(1))

    assert borrower.active_loan_count() == 3
    assert len(borrower._loans) == 3

    with pytest.raises(LoanLimitExceeded):
        borrower.issue_loan("loan-4", "eq-4", LoanPeriod(2))

    assert len(borrower._loans) == 3


def test_T4_BR4_eligibility():
    # T4: STUDENT + restricted equipment raises NotEligible; STAFF + restricted passes; STUDENT + non-restricted passes.
    eligibility_service = BorrowingEligibilityService()
    student = Borrower("b-2", "Ben", BorrowerType.STUDENT)
    staff = Borrower("b-3", "Cara", BorrowerType.STAFF)
    restricted_equipment = Equipment("eq-10", "Laser cutter", restricted=True)
    unrestricted_equipment = Equipment("eq-11", "Laptop", restricted=False)

    with pytest.raises(NotEligible):
        eligibility_service.check(student, restricted_equipment)

    eligibility_service.check(staff, restricted_equipment)
    eligibility_service.check(student, unrestricted_equipment)


def test_T5_BR5_equipment_follow_up():
    # T5: mark_on_loan() succeeds when AVAILABLE and raises EquipmentUnavailable when already ON_LOAN.
    equipment = Equipment("eq-12", "Microscope")
    equipment.mark_on_loan()
    assert equipment.status == EquipmentStatus.ON_LOAN

    with pytest.raises(EquipmentUnavailable):
        equipment.mark_on_loan()
