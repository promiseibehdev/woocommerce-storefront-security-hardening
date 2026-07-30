"""Reusable, side-effect-free domain validation helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from .errors import DomainValidationError, ValidationIssue

MONEY_QUANTUM = Decimal("0.01")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9.-]+)?$")
IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+$")
SUPPORTED_COUNTRY_CODES = frozenset({"NG", "GB", "US", "CA"})


class Validator:
    """Collect validation issues and raise one useful error per model."""

    def __init__(self, model: str) -> None:
        self.model = model
        self._issues: list[ValidationIssue] = []

    def require(self, condition: bool, field: str, message: str) -> None:
        if not condition:
            self._issues.append(ValidationIssue(field, message))

    def text(self, value: str, field: str, *, maximum: int = 500) -> None:
        self.require(isinstance(value, str) and bool(value.strip()), field, "must not be blank")
        if isinstance(value, str):
            self.require(len(value) <= maximum, field, f"must be at most {maximum} characters")

    def identifier(self, value: str, field: str = "id") -> None:
        self.text(value, field, maximum=64)
        if isinstance(value, str):
            self.require(bool(IDENTIFIER_PATTERN.fullmatch(value)), field, "has an invalid format")

    def finish(self) -> None:
        if self._issues:
            raise DomainValidationError(self.model, tuple(self._issues))


def money(value: Decimal) -> Decimal:
    if not isinstance(value, Decimal):
        raise TypeError("money values must use Decimal")
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def is_utc_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def normalize_utc(value: datetime) -> datetime:
    if not is_utc_aware(value):
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(UTC)


def is_valid_slug(value: str) -> bool:
    return bool(SLUG_PATTERN.fullmatch(value))


def is_valid_version(value: str) -> bool:
    return bool(VERSION_PATTERN.fullmatch(value))


def is_fictional_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value)) and value.lower().endswith("@example.test")


def is_reserved_test_url(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.hostname.endswith(".test")
    )


def is_safe_local_asset(value: str) -> bool:
    if not value or "\\" in value:
        return False
    parsed = urlsplit(value)
    path = PurePosixPath(value)
    return (
        not parsed.scheme
        and not parsed.netloc
        and not path.is_absolute()
        and ".." not in path.parts
        and path.suffix.lower() in {".png", ".webp", ".jpg", ".jpeg", ".svg"}
    )


def duplicates(values: Iterable[str]) -> frozenset[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return frozenset(repeated)


def safe_metadata(value: Mapping[str, Any]) -> bool:
    forbidden = {"password", "token", "cookie", "secret", "card_number", "cvv", "api_key"}
    return all(
        isinstance(key, str)
        and key.lower() not in forbidden
        and isinstance(item, (str, int, float, bool, type(None)))
        for key, item in value.items()
    )


def valid_date_order(start: date | datetime, end: date | datetime) -> bool:
    return start <= end
