"""Small pure utilities shared across future application layers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from decimal import Decimal

from .domain.validation import money

_WHITESPACE = re.compile(r"\s+")


def normalize_search_text(value: str) -> str:
    """Normalize display text for deterministic case-insensitive matching."""
    return _WHITESPACE.sub(" ", value.strip()).casefold()


def stable_unique(values: Iterable[str]) -> tuple[str, ...]:
    """Return first-seen nonblank values without duplicates."""
    return tuple(dict.fromkeys(value for value in values if value))


def sum_money(values: Iterable[Decimal]) -> Decimal:
    """Sum and quantize monetary values without floating-point arithmetic."""
    return money(sum(values, start=Decimal("0")))
