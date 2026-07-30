from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from woo_security_simulator.errors import (
    BackupError,
    CorruptDataError,
    MissingDataError,
    PersistenceError,
    UnsupportedSchemaError,
)
from woo_security_simulator.sample_data import build_sample_state
from woo_security_simulator.storage.json_store import JsonStateStore
from woo_security_simulator.storage.migrations import migrate_payload

NOW = datetime(2026, 7, 30, tzinfo=UTC)


def test_store_construction_and_missing_load_create_nothing(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "state.json"
    store = JsonStateStore(path)
    assert not path.parent.exists()
    with pytest.raises(MissingDataError):
        store.load()
    assert not path.parent.exists()
    assert store.list_backups() == ()


def test_save_load_round_trip_and_schema_envelope(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = JsonStateStore(path)
    state = build_sample_state()
    store.save(state, saved_at=NOW)
    assert store.load() == state
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert set(envelope) == {"schema_version", "application", "version", "saved_at", "payload"}
    assert envelope["schema_version"] == 1
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("content", ["", "{broken"])
def test_empty_and_malformed_files_are_preserved(tmp_path: Path, content: str) -> None:
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(CorruptDataError):
        JsonStateStore(path).load()
    assert path.read_text(encoding="utf-8") == content


def test_future_schema_fails_safely(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = JsonStateStore(path)
    store.save(build_sample_state(), saved_at=NOW)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["schema_version"] = 2
    path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(UnsupportedSchemaError):
        store.load()


def test_invalid_payload_fails_without_replacement(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = JsonStateStore(path)
    store.save(build_sample_state(), saved_at=NOW)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["payload"]["products"][0]["sku"] = ""
    path.write_text(json.dumps(envelope), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(CorruptDataError):
        store.load()
    assert path.read_bytes() == before


def test_save_creates_backup_and_retention_is_bounded(tmp_path: Path) -> None:
    store = JsonStateStore(tmp_path / "state.json", backup_retention=2)
    state = build_sample_state()
    for index in range(4):
        store.save(state, saved_at=NOW + timedelta(seconds=index))
    backups = store.list_backups()
    assert len(backups) == 2
    assert backups == tuple(sorted(backups, key=lambda item: item.name, reverse=True))


def test_validated_backup_restore_and_outside_path_rejection(tmp_path: Path) -> None:
    store = JsonStateStore(tmp_path / "state.json")
    original = build_sample_state()
    store.save(original, saved_at=NOW)
    backup = store.create_backup(timestamp=NOW + timedelta(seconds=1))
    store.path.write_text("{corrupt", encoding="utf-8")
    restored = store.restore(backup)
    assert restored == original
    assert store.load() == original
    assert len(tuple(tmp_path.glob("state.corrupt.*.json"))) == 1
    outside = tmp_path / "outside.json"
    outside.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(BackupError):
        store.restore(outside)


def test_corrupt_source_cannot_be_backed_up(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(CorruptDataError):
        JsonStateStore(path).create_backup()
    assert not (tmp_path / "backups").exists()


def test_schema_one_needs_no_migration() -> None:
    payload = {"value": 1}
    assert migrate_payload(payload, 1) is payload
    with pytest.raises(UnsupportedSchemaError):
        migrate_payload(payload, 2)


def test_atomic_replace_failure_preserves_destination_and_cleans_temp(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = JsonStateStore(path)
    state = build_sample_state()
    store.save(state, saved_at=NOW)
    original = path.read_bytes()
    with (
        patch(
            "woo_security_simulator.storage.json_store.os.replace",
            side_effect=OSError("simulated replacement failure"),
        ),
        pytest.raises(PersistenceError, match="atomic save failed"),
    ):
        store.save(state, saved_at=NOW + timedelta(days=1))
    assert path.read_bytes() == original
    assert not tuple(tmp_path.glob("*.tmp"))
