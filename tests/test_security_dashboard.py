from woo_security_simulator.domain.enums import FindingStatus, RiskLevel, Severity
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.sample_data import build_sample_state
from woo_security_simulator.services.security_dashboard import SecurityDashboardService


def dashboard() -> SecurityDashboardService:
    return SecurityDashboardService(UnitOfWork(build_sample_state()))


def test_overview_exact_summary() -> None:
    summary = dashboard().overview()
    assert summary.before.score == 35
    assert summary.before.risk_band is RiskLevel.HIGH
    assert summary.after.score == 83
    assert summary.after.risk_band is RiskLevel.GUARDED
    assert summary.improvement == 48
    assert summary.critical_findings == 1
    assert summary.high_findings == 1
    assert summary.passed_controls == 18
    assert summary.failed_controls == 4
    assert summary.remediated_findings == 10
    assert summary.quick_wins == 3


def test_component_summaries_cover_core_plugins_and_themes() -> None:
    components = dashboard().components()
    assert len(components) == 16
    assert {item.kind for item in components} >= {
        "wordpress",
        "woocommerce",
        "php",
        "plugin",
        "theme",
    }
    abandoned = next(item for item in components if item.id == "plugin_07")
    assert abandoned.lifecycle == "abandoned"
    assert abandoned.risk.level is RiskLevel.HIGH
    child = next(item for item in components if item.id == "theme_child")
    assert child.child_theme
    assert child.lifecycle == "child theme"


def test_finding_search_and_filters_use_after_snapshot_status() -> None:
    service = dashboard()
    assert len(service.findings()) == 14
    assert len(service.findings(status=FindingStatus.REMEDIATED)) == 10
    assert len(service.findings(status=FindingStatus.OPEN)) == 4
    critical_open = service.findings(
        severity=Severity.CRITICAL,
        status=FindingStatus.OPEN,
    )
    assert [item.finding.id for item in critical_open] == ["finding_13"]
    assert [item.finding.id for item in service.findings(search="retention")] == ["finding_13"]
    assert service.findings(category_id="security_privacy")


def test_hardening_plan_completed_remaining_and_quick_wins() -> None:
    service = dashboard()
    plan = service.hardening_plan()
    assert len(plan) == 14
    assert sum(item.completed for item in plan) == 10
    assert sum(not item.completed for item in plan) == 4
    assert len(service.quick_wins()) == 3
    assert all(not item.completed for item in service.quick_wins())


def test_dashboard_comparison_matches_scoring_service() -> None:
    comparison = dashboard().comparison()
    assert comparison.before_score == 35
    assert comparison.after_score == 83
    assert comparison.score_change == 48
    assert len(comparison.findings_remediated) == 10
    assert len(comparison.controls_improved) == 10
