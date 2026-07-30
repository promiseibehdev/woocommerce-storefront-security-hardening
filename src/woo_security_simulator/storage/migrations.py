"""Explicit schema migration registry; version 1 currently needs no migration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..errors import UnsupportedSchemaError
from ..metadata import DOMAIN_SCHEMA_VERSION

Migration = Callable[[dict[str, Any]], dict[str, Any]]
MIGRATIONS: dict[int, Migration] = {}


def migrate_payload(payload: dict[str, Any], source_version: int) -> dict[str, Any]:
    if source_version == DOMAIN_SCHEMA_VERSION:
        return payload
    if source_version > DOMAIN_SCHEMA_VERSION or source_version < 1:
        raise UnsupportedSchemaError(
            f"schema {source_version} is unsupported; expected {DOMAIN_SCHEMA_VERSION}"
        )
    current = source_version
    migrated = payload
    while current < DOMAIN_SCHEMA_VERSION:
        migration = MIGRATIONS.get(current)
        if migration is None:
            raise UnsupportedSchemaError(f"no explicit migration from schema {current}")
        migrated = migration(migrated)
        current += 1
    return migrated
