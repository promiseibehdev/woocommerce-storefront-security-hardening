from datetime import datetime
from decimal import Decimal

import pytest

from woo_security_simulator.domain.commerce import Product
from woo_security_simulator.domain.errors import SerializationError
from woo_security_simulator.serialization import from_primitive, to_primitive


def test_every_model_round_trips(model_instances: tuple[object, ...]) -> None:
    for model in model_instances:
        payload = to_primitive(model)
        assert isinstance(payload, dict)
        restored = from_primitive(type(model), payload)
        assert restored == model


def test_primitives_encode_money_and_time_without_type_loss(
    model_instances: tuple[object, ...],
) -> None:
    product = next(model for model in model_instances if isinstance(model, Product))
    payload = to_primitive(product)
    assert payload["regular_price"] == "25.00"
    assert payload["created_at"] == "2026-07-30T12:00:00Z"
    assert payload["stock_status"] == "in_stock"
    assert isinstance(payload["tags"], list)


def test_deserializer_rejects_unknown_fields(model_instances: tuple[object, ...]) -> None:
    product = next(model for model in model_instances if isinstance(model, Product))
    payload = to_primitive(product)
    assert isinstance(payload, dict)
    payload["unexpected"] = True
    with pytest.raises(SerializationError, match="unknown fields"):
        from_primitive(Product, payload)


def test_deserializer_requires_decimal_strings(model_instances: tuple[object, ...]) -> None:
    product = next(model for model in model_instances if isinstance(model, Product))
    payload = to_primitive(product)
    assert isinstance(payload, dict)
    payload["regular_price"] = 25.0
    with pytest.raises(SerializationError, match="Decimal"):
        from_primitive(Product, payload)


def test_serializer_rejects_naive_datetime() -> None:
    with pytest.raises(SerializationError):
        to_primitive(datetime(2026, 1, 1))


def test_serializer_rejects_unsupported_values() -> None:
    with pytest.raises(SerializationError):
        to_primitive({Decimal("1")})
