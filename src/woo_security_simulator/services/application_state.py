"""Explicit per-session state coordination and persistence boundaries."""

from __future__ import annotations

from pathlib import Path

from ..repositories.unit_of_work import UnitOfWork
from ..sample_data.factory import build_sample_state
from ..sample_data.integrity import validate_integrity
from ..state import ApplicationState
from ..storage.json_store import JsonStateStore


class ApplicationStateService:
    def __init__(self, store: JsonStateStore | None = None) -> None:
        self.uow = UnitOfWork()
        self.store = store

    def load_sample_data(self) -> ApplicationState:
        state = build_sample_state()
        self.uow.replace_state(state)
        return self.uow.snapshot()

    def save(self) -> None:
        if self.store is None:
            raise ValueError("no explicit persistence store configured")
        state = self.uow.snapshot()
        validate_integrity(state)
        self.store.save(state)

    def load(self) -> ApplicationState:
        if self.store is None:
            raise ValueError("no explicit persistence store configured")
        state = self.store.load()
        self.uow.replace_state(state)
        return self.uow.snapshot()

    def backup(self) -> Path:
        if self.store is None:
            raise ValueError("no explicit persistence store configured")
        return self.store.create_backup()

    def restore(self, backup_path: Path) -> ApplicationState:
        if self.store is None:
            raise ValueError("no explicit persistence store configured")
        state = self.store.restore(backup_path)
        self.uow.replace_state(state)
        return self.uow.snapshot()

    def reset_empty(self) -> ApplicationState:
        self.uow.replace_state(ApplicationState.empty())
        return self.uow.snapshot()
