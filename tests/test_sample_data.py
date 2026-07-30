from dataclasses import replace

import pytest

from woo_security_simulator.errors import ConflictError
from woo_security_simulator.sample_data import build_sample_state, validate_integrity
from woo_security_simulator.serialization import to_primitive


def test_exact_sample_counts() -> None:
    state = build_sample_state()
    assert len(state.products) == 20
    assert len(state.categories) == 6
    assert len(state.customers) == 4
    assert len(state.orders) == 8
    assert len(state.plugins) == 11
    assert len(state.security_controls) == 22
    assert len(state.security_findings) == 14
    assert len(state.audit_snapshots) == 2
    assert len(state.backup_records) == 5
    assert len(state.activity_events) == 12


def test_sample_generation_is_deterministic() -> None:
    assert to_primitive(build_sample_state()) == to_primitive(build_sample_state())


def test_sample_merchandising_and_security_mix() -> None:
    state = build_sample_state()
    assert sum(item.featured for item in state.products) == 5
    assert sum(item.sale_price is not None for item in state.products) == 6
    assert sum(item.stock_status.value == "low_stock" for item in state.products) == 4
    assert sum(item.stock_status.value == "out_of_stock" for item in state.products) == 1
    assert len({item.status for item in state.orders}) >= 6
    assert any(item.status.value == "inactive" for item in state.plugins)
    assert any(item.abandoned for item in state.plugins)
    assert any(item.is_child_theme and item.status.value == "active" for item in state.themes)


def test_sample_identity_and_asset_privacy() -> None:
    state = build_sample_state()
    text = str(to_primitive(state))
    assert all(item.email.endswith("@example.test") for item in state.customers)
    assert all(item.email.endswith("@example.test") for item in state.user_accounts)
    assert "C:\\Users\\" not in text
    assert all("://" not in item.image_ref for item in state.products)


def test_integrity_rejects_duplicate_sku() -> None:
    state = build_sample_state()
    duplicate = replace(state.products[1], sku=state.products[0].sku)
    broken = replace(state, products=(state.products[0], duplicate, *state.products[2:]))
    with pytest.raises(ConflictError, match="duplicate product SKU"):
        validate_integrity(broken)


def test_integrity_rejects_broken_category_reference() -> None:
    state = build_sample_state()
    broken_product = replace(state.products[0], category_id="category_missing")
    with pytest.raises(ConflictError, match="invalid product category"):
        validate_integrity(replace(state, products=(broken_product, *state.products[1:])))
