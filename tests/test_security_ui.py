from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from woo_security_simulator.ui.shell import SECURITY_NAVIGATION
from woo_security_simulator.ui.state import SERVICE_KEY

APP_PATH = Path(__file__).parents[1] / "app.py"


def _button(app: AppTest, label: str):
    matches = [button for button in app.button if button.label == label]
    assert matches, f"button not found: {label}"
    return matches[-1]


def _security_app(*, load: bool = True) -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    _button(app, "Security").click().run()
    assert list(app.exception) == []
    if load:
        _button(app, "Load Fictional Sample Data").click().run()
        assert list(app.exception) == []
    return app


def test_security_navigation_is_exact_and_grouped() -> None:
    assert SECURITY_NAVIGATION == (
        "Security Overview",
        "Components",
        "Findings",
        "Hardening",
        "Reports",
    )


def test_security_workspace_starts_empty_without_loading_samples() -> None:
    app = _security_app(load=False)
    service = app.session_state[SERVICE_KEY]
    assert service.uow.dataset_id == "empty"
    assert service.uow.security_findings.count() == 0
    assert "Load Fictional Sample Data" in [button.label for button in app.button]
    assert "No sample data is loaded." in [warning.value for warning in app.warning]


def test_overview_renders_exact_scores_controls_and_disclaimer() -> None:
    app = _security_app()
    metrics = {(metric.label, metric.value) for metric in app.metric}
    assert metrics >= {
        ("Overall Security Score", "83/100"),
        ("Risk Band", "Guarded"),
        ("Before Score", "35"),
        ("After Score", "83"),
        ("Improvement", "+48"),
        ("Critical Findings", "1"),
        ("High Findings", "1"),
        ("Passed Controls", "18"),
        ("Failed Controls", "4"),
        ("Remediated Findings", "10"),
        ("Quick Wins", "3"),
    }
    assert any("not an industry certification" in item.value for item in app.warning)


@pytest.mark.parametrize(
    "destination",
    ("Security Overview", "Components", "Findings", "Hardening", "Reports"),
)
def test_each_security_destination_renders(destination: str) -> None:
    app = _security_app()
    _button(app, destination).click().run()
    assert list(app.exception) == []
    assert destination in [title.value for title in app.title]


def test_components_render_core_plugin_theme_and_lifecycle_content() -> None:
    app = _security_app()
    _button(app, "Components").click().run()
    text = " ".join(item.value for item in app.markdown)
    assert "WordPress Core" in text
    assert "WooCommerce" in text
    assert "PHP" in text
    assert "Northstar Legacy Gallery" in text
    assert "Northstar Child" in text
    assert "Child-theme status" in text
    assert any(control.label == "Plugin lifecycle" for control in app.selectbox)


def test_findings_have_search_and_all_required_filters() -> None:
    app = _security_app()
    _button(app, "Findings").click().run()
    assert [control.label for control in app.text_input] == ["Search findings"]
    assert {control.label for control in app.selectbox} >= {
        "Severity",
        "Category",
        "Status",
    }
    severity = next(control for control in app.selectbox if control.label == "Severity")
    severity.select("critical").run()
    assert list(app.exception) == []
    assert any("findings shown" in item.value for item in app.markdown)


def test_hardening_renders_completed_remaining_and_quick_wins() -> None:
    app = _security_app()
    _button(app, "Hardening").click().run()
    metrics = {(metric.label, metric.value) for metric in app.metric}
    assert metrics >= {
        ("Plan Items", "14"),
        ("Quick Wins", "3"),
        ("Completed", "10"),
        ("Remaining", "4"),
    }
    assert {tab.label for tab in app.tabs} == {
        "Prioritized Plan",
        "Quick Wins",
        "Completed",
        "Remaining",
    }


def test_reports_render_comparison_json_export_privacy_and_warnings() -> None:
    app = _security_app()
    _button(app, "Reports").click().run()
    metrics = {(metric.label, metric.value) for metric in app.metric}
    assert metrics >= {
        ("Before", "35"),
        ("After", "83"),
        ("Score Change", "+48"),
    }
    downloads = app.get("download_button")
    assert len(downloads) == 1
    assert downloads[0].label == "Download fictional security report (JSON)"
    page_text = " ".join(
        item.value
        for collection in (
            app.subheader,
            app.markdown,
            app.warning,
            app.info,
            app.caption,
        )
        for item in collection
    )
    assert "Privacy statement" in page_text
    assert "Hosted persistence warning" in page_text
    assert "PDF export is not implemented" in page_text


def test_security_ui_has_text_statuses_and_responsive_shared_styles() -> None:
    root = APP_PATH.parent
    source = (root / "src" / "woo_security_simulator" / "ui" / "security_pages.py").read_text(
        encoding="utf-8"
    )
    styles = (root / "src" / "woo_security_simulator" / "ui" / "styles.py").read_text(
        encoding="utf-8"
    )
    for text in ("Critical", "High", "Current status", "Risk", "Estimated effort"):
        assert text in source
    assert "@media (max-width: 640px)" in styles
