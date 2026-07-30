from pathlib import Path

from streamlit.testing.v1 import AppTest

from woo_security_simulator.ui.state import SERVICE_KEY

APP_PATH = Path(__file__).parents[1] / "app.py"


def _button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def test_streamlit_sessions_do_not_share_sample_cart_or_selection() -> None:
    first = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    _button(first, "Load Fictional Sample Data").click().run()
    _button(first, "Add").click().run()
    first_service = first.session_state[SERVICE_KEY]
    assert first_service.uow.dataset_id == "northstar-v1"
    assert first_service.uow.carts.get("cart_customer_01").items

    second = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    second_service = second.session_state[SERVICE_KEY]
    assert second_service is not first_service
    assert second_service.uow.dataset_id == "empty"
    assert second_service.uow.products.count() == 0
    assert second_service.uow.carts.count() == 0


def test_distinct_application_state_services_have_isolated_security_state() -> None:
    first = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    second = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    _button(first, "Load Fictional Sample Data").click().run()
    assert first.session_state[SERVICE_KEY].uow.security_findings.count() == 14
    assert second.session_state[SERVICE_KEY].uow.security_findings.count() == 0
