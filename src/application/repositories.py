from abc import ABC, abstractmethod


class BorrowerRepository(ABC):
    """BR6: repository contract for borrowers."""

    @abstractmethod
    def get(self, borrower_id):
        pass

    @abstractmethod
    def save(self, borrower):
        pass


class EquipmentRepository(ABC):
    """BR6: repository contract for equipment."""

    @abstractmethod
    def get(self, equipment_id):
        pass

    @abstractmethod
    def save(self, equipment):
        pass
