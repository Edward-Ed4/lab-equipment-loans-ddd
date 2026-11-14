from src.domain.enums import EquipmentStatus
from src.domain.errors import EquipmentUnavailable


class Equipment:
    """BR5 - equipment can be ON_LOAN for only one loan at a time"""

    def __init__(self, equipment_id: str, name: str, restricted: bool = False):
        self.equipment_id = equipment_id
        self.name = name
        self.restricted = restricted
        self.status = EquipmentStatus.AVAILABLE

    def mark_on_loan(self):
        if self.status != EquipmentStatus.AVAILABLE:
            raise EquipmentUnavailable("Equipment is not available for loan.")
        self.status = EquipmentStatus.ON_LOAN

    def __eq__(self, other):
        return isinstance(other, Equipment) and self.equipment_id == other.equipment_id

    def __hash__(self):
        return hash(self.equipment_id)
