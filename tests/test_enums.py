from enum import StrEnum

import pytest

from woo_security_simulator.domain import enums


def test_all_declared_enums_are_string_enums_with_unique_values() -> None:
    enum_types = [
        value
        for value in vars(enums).values()
        if isinstance(value, type) and issubclass(value, StrEnum) and value is not StrEnum
    ]
    assert len(enum_types) == 28
    for enum_type in enum_types:
        values = [member.value for member in enum_type]
        assert values
        assert len(values) == len(set(values))
        assert all(value == value.lower() for value in values)


def test_enum_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        enums.StockStatus("available-ish")
