from datetime import UTC, datetime

import pytest

from woo_security_simulator.domain.errors import DomainValidationError
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.services.activity import ActivityService


def test_activity_records_only_after_explicit_action() -> None:
    uow = UnitOfWork()
    service = ActivityService(uow)
    assert uow.activity_events.count() == 0
    event = service.record(
        "event_explicit",
        datetime(2026, 7, 30, tzinfo=UTC),
        "Fictional sample data loaded.",
        metadata={"dataset_id": "northstar-v1"},
    )
    assert uow.activity_events.list() == (event,)


def test_activity_rejects_sensitive_metadata_keys() -> None:
    service = ActivityService(UnitOfWork())
    with pytest.raises(DomainValidationError):
        service.record(
            "event_unsafe",
            datetime(2026, 7, 30, tzinfo=UTC),
            "Unsafe event.",
            metadata={"token": "not-allowed"},
        )
