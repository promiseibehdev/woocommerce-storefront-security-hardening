from datetime import UTC, datetime

import pytest

from woo_security_simulator.domain.enums import (
    FindingStatus,
    RemediationStatus,
    RiskLevel,
    VerificationStatus,
)
from woo_security_simulator.errors import ReportError
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.sample_data import build_sample_state
from woo_security_simulator.services.report import SecurityReportService
from woo_security_simulator.services.security import (
    ComparisonService,
    FindingService,
    RiskService,
    SecurityScoringService,
)

NOW = datetime(2026, 7, 30, tzinfo=UTC)


@pytest.fixture
def uow() -> UnitOfWork:
    return UnitOfWork(build_sample_state())


def test_component_plugin_and_theme_risk_is_explainable(uow: UnitOfWork) -> None:
    risk = RiskService()
    assert risk.component(uow.core_components.get("component_php")).reasons
    abandoned = risk.plugin(uow.plugins.get("plugin_07"))
    assert abandoned.level is RiskLevel.HIGH
    assert any("abandoned" in reason for reason in abandoned.reasons)
    child = risk.theme(uow.themes.get("theme_child"), uow.themes.list())
    assert child.level is RiskLevel.LOW


def test_exact_before_and_after_scores_and_bands(uow: UnitOfWork) -> None:
    scoring = SecurityScoringService(uow)
    before = scoring.score_snapshot(uow.audit_snapshots.get("snapshot_before"))
    after = scoring.score_snapshot(uow.audit_snapshots.get("snapshot_after"))
    assert before.score == 35
    assert before.risk_band is RiskLevel.HIGH
    assert before.risk_points == 64
    assert after.score == 83
    assert after.risk_band is RiskLevel.GUARDED
    assert after.risk_points == 17
    assert before.maximum_points == after.maximum_points == 98


def test_linked_controls_do_not_duplicate_finding_risk(uow: UnitOfWork) -> None:
    before = SecurityScoringService(uow).score_snapshot(uow.audit_snapshots.get("snapshot_before"))
    assert before.risk_points == 64
    assert before.maximum_points == 98


def test_findings_filter_group_prioritize_quick_wins_and_updates(uow: UnitOfWork) -> None:
    service = FindingService(uow)
    assert len(service.list()) == 14
    assert service.group_by_severity()["critical"]
    assert len(service.group_by_category()) == 6
    assert service.prioritized()[0].severity.value == "critical"
    assert service.quick_wins()
    assert sum(service.effort_summary().values()) == 14
    action = service.update_remediation("action_01", RemediationStatus.COMPLETED, completed_at=NOW)
    assert action.status is RemediationStatus.COMPLETED
    finding = service.mark_finding(
        "finding_01",
        FindingStatus.REMEDIATED,
        after_state="Verified hardened state.",
        verification_status=VerificationStatus.VERIFIED,
    )
    assert finding.status is FindingStatus.REMEDIATED


def test_comparison_reports_improvements_and_remaining_high_risk(uow: UnitOfWork) -> None:
    comparison = ComparisonService(uow).compare(
        uow.audit_snapshots.get("snapshot_before"),
        uow.audit_snapshots.get("snapshot_after"),
    )
    assert comparison.score_change == 48
    assert len(comparison.findings_remediated) == 10
    assert len(comparison.controls_improved) == 10
    assert comparison.controls_regressed == ()
    assert set(comparison.component_version_improvements) == {"wordpress", "woocommerce", "php"}
    assert comparison.plugin_risk_improvements == ("plugin_07",)
    assert comparison.remaining_critical_high


def test_report_is_deterministic_valid_and_private(uow: UnitOfWork) -> None:
    service = SecurityReportService(uow)
    first = service.generate(audited_at=NOW)
    second = service.generate(audited_at=NOW)
    assert first == second
    assert '"score": 83' in first
    assert "fictional" in first.casefold()
    assert "C:\\\\Users\\\\" not in first
    assert "card_number" not in first
    assert "api_key" not in first
    assert "northstar.example.test" not in first


def test_empty_report_fails_clearly() -> None:
    with pytest.raises(ReportError):
        SecurityReportService(UnitOfWork()).generate(audited_at=NOW)
