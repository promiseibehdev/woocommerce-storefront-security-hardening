"""Safe fictional activity recording."""

from __future__ import annotations

from datetime import datetime

from ..domain.enums import ActivityEventType, ActivityOutcome
from ..domain.security import ActivityEvent
from ..repositories.unit_of_work import UnitOfWork


class ActivityService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def record(
        self,
        event_id: str,
        occurred_at: datetime,
        summary: str,
        *,
        event_type: ActivityEventType = ActivityEventType.SECURITY_REVIEW,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> ActivityEvent:
        event = ActivityEvent(
            event_id,
            occurred_at,
            "Northstar simulator",
            event_type,
            summary,
            ActivityOutcome.SUCCESS,
            metadata=metadata or {},
        )
        self.uow.activity_events.add(event)
        return event
