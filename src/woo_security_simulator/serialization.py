"""Explicit JSON-compatible serialization for domain dataclasses."""

from __future__ import annotations

import types
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Union, get_args, get_origin, get_type_hints

from .domain.errors import SerializationError

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def to_primitive(value: Any) -> JsonValue:
    """Convert supported domain values to deterministic JSON-compatible primitives."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise SerializationError("cannot serialize a naive datetime")
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: to_primitive(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise SerializationError("mapping keys must be strings")
        return {key: to_primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [to_primitive(item) for item in value]
    raise SerializationError(f"unsupported value type: {type(value).__name__}")


def from_primitive[T](model_type: type[T], payload: Mapping[str, JsonValue]) -> T:
    """Reconstruct one declared dataclass type from untrusted primitive input."""
    if not is_dataclass(model_type):
        raise SerializationError("model_type must be a dataclass type")
    if not isinstance(payload, Mapping):
        raise SerializationError("payload must be a mapping")
    hints = get_type_hints(model_type)
    declared = {item.name for item in fields(model_type)}
    unknown = set(payload) - declared
    if unknown:
        raise SerializationError(f"unknown fields for {model_type.__name__}: {sorted(unknown)}")
    values: dict[str, Any] = {}
    for item in fields(model_type):
        if item.name in payload:
            try:
                values[item.name] = _convert(hints[item.name], payload[item.name])
            except (TypeError, ValueError, InvalidOperation, KeyError) as exc:
                raise SerializationError(
                    f"invalid {model_type.__name__}.{item.name}: {exc}"
                ) from exc
    try:
        return model_type(**values)
    except (TypeError, ValueError) as exc:
        raise SerializationError(f"invalid {model_type.__name__} payload: {exc}") from exc


def _convert(annotation: Any, value: JsonValue) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in {Union, types.UnionType}:
        if value is None and type(None) in args:
            return None
        errors: list[Exception] = []
        for option in (item for item in args if item is not type(None)):
            try:
                return _convert(option, value)
            except (TypeError, ValueError, InvalidOperation, KeyError, SerializationError) as exc:
                errors.append(exc)
        raise SerializationError(f"value did not match union: {errors[-1] if errors else value}")
    if value is None:
        raise SerializationError("null is not allowed")
    if annotation is Any:
        return value
    if annotation is Decimal:
        if not isinstance(value, str):
            raise SerializationError("Decimal must be encoded as a string")
        return Decimal(value)
    if annotation is datetime:
        if not isinstance(value, str):
            raise SerializationError("datetime must be encoded as a string")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise SerializationError("datetime must include a timezone")
        return parsed.astimezone(UTC)
    if annotation is date:
        if not isinstance(value, str):
            raise SerializationError("date must be encoded as a string")
        return date.fromisoformat(value)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return annotation(value)
    if isinstance(annotation, type) and is_dataclass(annotation):
        if not isinstance(value, Mapping):
            raise SerializationError("nested model must be an object")
        return from_primitive(annotation, value)
    if origin in {tuple, list}:
        if not isinstance(value, list):
            raise SerializationError("sequence must be encoded as a list")
        converted = [_convert(args[0], item) for item in value]
        return tuple(converted) if origin is tuple else converted
    if origin is dict:
        if not isinstance(value, Mapping):
            raise SerializationError("dictionary must be encoded as an object")
        key_type, item_type = args
        if key_type is not str:
            raise SerializationError("only string-key dictionaries are supported")
        return {str(key): _convert(item_type, item) for key, item in value.items()}
    if annotation is bool:
        if type(value) is not bool:
            raise SerializationError("expected boolean")
        return value
    if annotation is int:
        if type(value) is not int:
            raise SerializationError("expected integer")
        return value
    if annotation is float:
        if type(value) not in {int, float}:
            raise SerializationError("expected number")
        return float(value)
    if annotation is str:
        if not isinstance(value, str):
            raise SerializationError("expected string")
        return value
    raise SerializationError(f"unsupported annotation: {annotation!r}")
