from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from woo_security_simulator.ui.shell import NAVIGATION
from woo_security_simulator.ui.state import SERVICE_KEY

APP_PATH = Path(__file__).parents[1] / "app.py"


def _run_empty() -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    assert list(app.exception) == []
    return app


def _button(app: AppTest, label: str):
    matches = [button for button in app.button if button.label == label]
    assert matches, f"button not found: {label}"
    return matches[-1]


def _load(app: AppTest) -> AppTest:
    _button(app, "Load Fictional Sample Data").click().run()
    assert list(app.exception) == []
    return app


def test_startup_is_empty_and_requires_explicit_load() -> None:
    app = _run_empty()
    service = app.session_state[SERVICE_KEY]
    assert service.uow.dataset_id == "empty"
    assert service.uow.products.count() == 0
    assert "Load Fictional Sample Data" in [button.label for button in app.button]
    assert [warning.value for warning in app.warning] == ["No sample data is loaded."]
    assert not service.uow.carts.list()


def test_explicit_load_populates_home_metrics() -> None:
    app = _load(_run_empty())
    service = app.session_state[SERVICE_KEY]
    assert service.uow.dataset_id == "northstar-v1"
    assert service.uow.products.count() == 20
    assert {(metric.label, metric.value) for metric in app.metric} >= {
        ("Products", "20"),
        ("Featured", "5"),
        ("On sale", "6"),
    }


def test_navigation_registry_contains_only_storefront_destinations() -> None:
    assert NAVIGATION == {
        "Browse": ("Store Home", "Shop", "Categories", "Product Details"),
        "Purchase": ("Shopping Cart", "Checkout", "Order Confirmation"),
        "My Store": ("My Account", "Order History", "Wishlist"),
        "Information": ("Store Information",),
    }
    assert "Security" not in str(NAVIGATION)


@pytest.mark.parametrize(
    "destination",
    (
        "Store Home",
        "Shop",
        "Categories",
        "Product Details",
        "Shopping Cart",
        "Checkout",
        "Order Confirmation",
        "My Account",
        "Order History",
        "Wishlist",
        "Store Information",
    ),
)
def test_every_storefront_destination_renders(destination: str) -> None:
    app = _load(_run_empty())
    _button(app, destination).click().run()
    assert list(app.exception) == []
    expected_title = "Northstar Desk & Living" if destination == "Store Home" else destination
    assert expected_title in [title.value for title in app.title]


def test_add_to_cart_and_cart_quantity_controls() -> None:
    app = _load(_run_empty())
    _button(app, "Add").click().run()
    assert list(app.exception) == []
    service = app.session_state[SERVICE_KEY]
    assert sum(item.quantity for item in service.uow.carts.get("cart_customer_01").items) == 1
    _button(app, "Shopping Cart").click().run()
    assert list(app.exception) == []
    assert "Shopping Cart" in [title.value for title in app.title]
    assert app.number_input
    assert any("Quantity for" in control.label for control in app.number_input)


def test_checkout_has_no_sensitive_inputs_and_places_simulated_order() -> None:
    app = _load(_run_empty())
    _button(app, "Add").click().run()
    assert list(app.exception) == []
    _button(app, "Checkout").click().run()
    assert list(app.exception) == []
    assert "Simulation only. No real payment is processed." in [
        warning.value for warning in app.warning
    ]
    input_labels = " ".join(
        control.label
        for collection in (app.text_input, app.number_input, app.text_area)
        for control in collection
    ).casefold()
    for forbidden in ("card number", "cvv", "banking credential", "address"):
        assert forbidden not in input_labels
    agreement = next(
        control for control in app.checkbox if control.label.startswith("I understand")
    )
    agreement.check().run()
    _button(app, "Place simulated order").click().run()
    assert list(app.exception) == []
    assert "Order Confirmation" in [title.value for title in app.title]
    assert any("Simulated order placed successfully" in item.value for item in app.success)
    assert "Simulation only. No real payment is processed." in [
        warning.value for warning in app.warning
    ]


def test_responsive_css_and_accessible_status_contract() -> None:
    root = APP_PATH.parent
    styles = (root / "src" / "woo_security_simulator" / "ui" / "styles.py").read_text(
        encoding="utf-8"
    )
    components = (root / "src" / "woo_security_simulator" / "ui" / "components.py").read_text(
        encoding="utf-8"
    )
    assert "@media (max-width: 640px)" in styles
    assert "In stock" in components
    assert "Low stock" in components
    assert "Out of stock" in components
