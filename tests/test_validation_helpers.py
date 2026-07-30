from datetime import UTC, datetime
from decimal import Decimal

import pytest

from woo_security_simulator.domain.errors import DomainValidationError
from woo_security_simulator.domain.validation import (
    Validator,
    duplicates,
    is_fictional_email,
    is_reserved_test_url,
    is_safe_local_asset,
    money,
)
from woo_security_simulator.utilities import normalize_search_text, stable_unique, sum_money


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("assets/products/item.webp", True),
        ("../secret.png", False),
        ("https://example.test/item.png", False),
        ("C:\\item.png", False),
        ("assets/item.exe", False),
    ],
)
def test_local_asset_validation(value: str, expected: bool) -> None:
    assert is_safe_local_asset(value) is expected


def test_fictional_identity_boundaries() -> None:
    assert is_fictional_email("demo@example.test")
    assert not is_fictional_email("person@invalid.test")
    assert is_reserved_test_url("https://store.example.test")
    assert not is_reserved_test_url("https://invalid.example")


def test_money_and_shared_utilities_are_deterministic() -> None:
    assert money(Decimal("1.005")) == Decimal("1.01")
    assert sum_money([Decimal("1.005"), Decimal("2.005")]) == Decimal("3.01")
    assert normalize_search_text("  Meridian   DOCK ") == "meridian dock"
    assert stable_unique(["a", "", "b", "a"]) == ("a", "b")
    assert duplicates(["a", "b", "a"]) == frozenset({"a"})


def test_money_refuses_float() -> None:
    with pytest.raises(TypeError):
        money(1.2)  # type: ignore[arg-type]


def test_validator_reports_all_collected_issues() -> None:
    validator = Validator("Example")
    validator.require(False, "first", "failed")
    validator.require(False, "second", "also failed")
    with pytest.raises(DomainValidationError) as error:
        validator.finish()
    assert [issue.field for issue in error.value.issues] == ["first", "second"]


def test_timezone_helper_fixture_is_aware() -> None:
    assert datetime(2026, 1, 1, tzinfo=UTC).utcoffset() is not None
