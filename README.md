University lab equipment borrowing project.
This project models the issuance of equipment loans in a small, teachable domain for university coursework on Domain-Driven Design, TDD, and clean architecture.
It focuses on the borrowing flow: a request is validated, a loan is issued, and the equipment is marked on loan.

Folder overview:
- src/domain: domain model, value objects, enums, rules, and events
- src/application: service orchestration and DTOs
- src/infrastructure: in-memory repositories
- src/interface: composition root and demo entry point
- tests: pytest coverage for the domain and loan flow
- evidence: saved test evidence and run outputs

Python version used: Python 3.14.6 (tested); 3.11+ should work

Test command: `python -m pytest -v`
The suite contains T1-T8 (the eight coursework tests) plus 2 architecture checks in tests/test_architecture.py (10 tests in total).
Evidence folder: [evidence](evidence)

Business rules:
- BR1 LoanPeriod
- BR2 Loan
- BR3 Borrower (aggregate root)
- BR4 BorrowingEligibilityService
- BR5 LoanIssued event -> LoanIssuedHandler -> Equipment (aggregate root)
- BR6 BorrowerRepository / EquipmentRepository + IssueLoanService
