class DomainError(Exception):
    pass


class InvalidLoanPeriod(DomainError):
    pass


class InvalidLoanTransition(DomainError):
    pass


class LoanLimitExceeded(DomainError):
    pass


class NotEligible(DomainError):
    pass


class EquipmentUnavailable(DomainError):
    pass
