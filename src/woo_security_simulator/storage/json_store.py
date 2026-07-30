"""Atomic, validated, opt-in JSON state persistence."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..errors import (
    BackupError,
    CorruptDataError,
    MissingDataError,
    PersistenceError,
    UnsupportedSchemaError,
)
from ..metadata import APPLICATION_NAME, APPLICATION_VERSION, DOMAIN_SCHEMA_VERSION
from ..sample_data.integrity import validate_integrity
from ..serialization import SerializationError, from_primitive, to_primitive
from ..state import ApplicationState
from .envelope import SchemaEnvelope
from .migrations import migrate_payload


class JsonStateStore:
    """Creates no directories or files until save/backup/restore is called."""

    def __init__(self, path: Path, *, backup_retention: int = 5) -> None:
        if backup_retention < 1:
            raise ValueError("backup_retention must be positive")
        self.path = Path(path)
        self.backup_retention = backup_retention

    @property
    def backup_directory(self) -> Path:
        return self.path.parent / "backups"

    def save(self, state: ApplicationState, *, saved_at: datetime | None = None) -> None:
        validate_integrity(state)
        timestamp = (saved_at or datetime.now(UTC)).astimezone(UTC)
        envelope = SchemaEnvelope(
            schema_version=DOMAIN_SCHEMA_VERSION,
            application=APPLICATION_NAME,
            version=APPLICATION_VERSION,
            saved_at=timestamp,
            payload=to_primitive(state),
        )
        encoded = (
            json.dumps(
                to_primitive(envelope),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.create_backup(timestamp=timestamp)
        self._atomic_replace(encoded)

    def load(self) -> ApplicationState:
        if not self.path.exists():
            raise MissingDataError(f"state file does not exist: {self.path.name}")
        return self._load_path(self.path)

    def create_backup(self, *, timestamp: datetime | None = None) -> Path:
        if not self.path.exists():
            raise BackupError("cannot back up a missing state file")
        self._load_path(self.path)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        value = (timestamp or datetime.now(UTC)).astimezone(UTC)
        suffix = value.strftime("%Y%m%dT%H%M%S%fZ")
        destination = self.backup_directory / f"{self.path.stem}-{suffix}.json"
        try:
            shutil.copy2(self.path, destination)
            self._prune_backups()
        except OSError as exc:
            raise BackupError("backup creation failed") from exc
        return destination

    def list_backups(self) -> tuple[Path, ...]:
        if not self.backup_directory.exists():
            return ()
        return tuple(
            sorted(
                self.backup_directory.glob(f"{self.path.stem}-*.json"),
                key=lambda path: path.name,
                reverse=True,
            )
        )

    def restore(self, backup_path: Path) -> ApplicationState:
        candidate = Path(backup_path)
        try:
            candidate.resolve().relative_to(self.backup_directory.resolve())
        except (OSError, ValueError) as exc:
            raise BackupError("backup path is outside the managed backup directory") from exc
        state = self._load_path(candidate)
        encoded = candidate.read_text(encoding="utf-8")
        if self.path.exists():
            try:
                self._load_path(self.path)
            except CorruptDataError:
                corrupt_name = (
                    f"{self.path.stem}.corrupt."
                    f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}{self.path.suffix}"
                )
                try:
                    shutil.copy2(self.path, self.path.with_name(corrupt_name))
                except OSError as exc:
                    raise BackupError("could not preserve corrupt state before restore") from exc
            else:
                self.create_backup()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._atomic_replace(encoded)
        return state

    def _load_path(self, path: Path) -> ApplicationState:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PersistenceError(f"could not read {path.name}") from exc
        if not text.strip():
            raise CorruptDataError(f"{path.name} is empty")
        try:
            envelope: dict[str, Any] = json.loads(text)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise CorruptDataError(f"{path.name} contains malformed JSON") from exc
        if not isinstance(envelope, dict):
            raise CorruptDataError("schema envelope must be an object")
        required = {"schema_version", "application", "version", "saved_at", "payload"}
        if set(envelope) != required:
            raise CorruptDataError("schema envelope fields are invalid")
        version = envelope["schema_version"]
        if type(version) is not int:
            raise CorruptDataError("schema_version must be an integer")
        if version > DOMAIN_SCHEMA_VERSION:
            raise UnsupportedSchemaError(
                f"schema {version} is newer than supported schema {DOMAIN_SCHEMA_VERSION}"
            )
        if envelope["application"] != APPLICATION_NAME:
            raise CorruptDataError("application identity does not match")
        payload = envelope["payload"]
        if not isinstance(payload, dict):
            raise CorruptDataError("payload must be an object")
        try:
            migrated = migrate_payload(payload, version)
            state = from_primitive(ApplicationState, migrated)
            validate_integrity(state)
        except (SerializationError, ValueError) as exc:
            raise CorruptDataError("stored application state is invalid") from exc
        return state

    def _atomic_replace(self, encoded: str) -> None:
        temporary: Path | None = None
        try:
            descriptor, raw_path = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
                text=True,
            )
            temporary = Path(raw_path)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except OSError as exc:
            raise PersistenceError(f"atomic save failed for {self.path.name}") from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def _prune_backups(self) -> None:
        for old_backup in self.list_backups()[self.backup_retention :]:
            try:
                old_backup.unlink()
            except OSError as exc:
                raise BackupError("backup retention cleanup failed") from exc
