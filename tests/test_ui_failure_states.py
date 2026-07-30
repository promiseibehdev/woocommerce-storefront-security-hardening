from pathlib import Path

from streamlit.testing.v1 import AppTest

from woo_security_simulator.ui.state import SERVICE_KEY

APP_PATH = Path(__file__).parents[1] / "app.py"


def _button(app: AppTest, label: str):
    matches = [button for button in app.button if button.label == label]
    assert matches
    return matches[-1]


def _loaded() -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    _button(app, "Load Fictional Sample Data").click().run()
    return app


def test_invalid_coupon_shows_safe_message_without_traceback() -> None:
    app = _loaded()
    _button(app, "Add").click().run()
    _button(app, "Checkout").click().run()
    coupon = next(
        control for control in app.text_input if control.label == "Coupon code (optional)"
    )
    coupon.input("NOT-A-COUPON").run()
    assert list(app.exception) == []
    assert any("Coupon or shipping validation" in error.value for error in app.error)


def test_missing_security_snapshot_uses_safe_page_boundary() -> None:
    app = _loaded()
    service = app.session_state[SERVICE_KEY]
    service.uow.audit_snapshots.delete("snapshot_before")
    _button(app, "Security").click().run()
    assert list(app.exception) == []
    assert any("temporarily unavailable" in error.value for error in app.error)


def test_empty_component_inventory_has_clear_empty_state() -> None:
    app = _loaded()
    service = app.session_state[SERVICE_KEY]
    service.uow.core_components.replace_all(())
    service.uow.plugins.replace_all(())
    service.uow.themes.replace_all(())
    _button(app, "Security").click().run()
    _button(app, "Components").click().run()
    assert list(app.exception) == []
    assert any("No component inventory" in item.value for item in app.markdown)


def test_missing_customer_context_does_not_expose_raw_exception() -> None:
    app = _loaded()
    _button(app, "Security").click().run()
    service = app.session_state[SERVICE_KEY]
    service.uow.customers.replace_all(())
    _button(app, "Storefront").click().run()
    _button(app, "My Account").click().run()
    assert list(app.exception) == []
    assert any("temporarily unavailable" in error.value for error in app.error)
