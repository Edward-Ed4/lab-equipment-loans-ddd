from src.application.repositories import BorrowerRepository, EquipmentRepository


class InMemoryBorrowerRepository(BorrowerRepository):
    """BR6: in-memory storage for borrowers."""

    def __init__(self):
        self._items = {}

    def get(self, borrower_id):
        return self._items.get(borrower_id)

    def save(self, borrower):
        self._items[borrower.borrower_id] = borrower


class InMemoryEquipmentRepository(EquipmentRepository):
    """BR6: in-memory storage for equipment."""

    def __init__(self):
        self._items = {}

    def get(self, equipment_id):
        return self._items.get(equipment_id)

    def save(self, equipment):
        self._items[equipment.equipment_id] = equipment
