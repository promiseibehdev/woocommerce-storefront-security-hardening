"""Versioned persistence envelope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SchemaEnvelope:
    schema_version: int
    application: str
    version: str
    saved_at: datetime
    payload: dict[str, Any]
