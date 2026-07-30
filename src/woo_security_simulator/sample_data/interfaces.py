"""Side-effect-free interfaces for Phase 3 sample-data implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..domain.commerce import CommerceModel
from ..domain.security import SecurityModel


@dataclass(frozen=True, slots=True)
class SampleDataBundle:
    """Immutable in-memory handoff contract; it does not create or persist data."""

    dataset_id: str
    schema_version: int
    commerce_records: tuple[CommerceModel, ...]
    security_records: tuple[SecurityModel, ...]
    fictional: bool = True


@runtime_checkable
class SampleDataProvider(Protocol):
    """Contract for explicit, deterministic sample construction."""

    @property
    def dataset_id(self) -> str: ...

    def build(self) -> SampleDataBundle:
        """Build in memory only after an explicit caller action."""
        ...
