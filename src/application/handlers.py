from dataclasses import dataclass

from src.domain.errors import EquipmentUnavailable


@dataclass
class HandlerResult:
    """BR5: result returned by a domain event handler."""

    success: bool
    reason: str


class LoanIssuedHandler:
    """BR5: marks equipment on loan when a LoanIssued event is published."""

    def __init__(self, equipment_repo):
        self.equipment_repo = equipment_repo

    def handle(self, event):
        try:
            equipment = self.equipment_repo.get(event.equipment_id)
            if equipment is None:
                return HandlerResult(False, "equipment-not-found")
            equipment.mark_on_loan()
            self.equipment_repo.save(equipment)
            return HandlerResult(True, "equipment-marked-on-loan")
        except EquipmentUnavailable as exc:
            return HandlerResult(False, str(exc))
