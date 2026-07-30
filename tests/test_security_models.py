from datetime import UTC, date, datetime

import pytest

from woo_security_simulator.domain.enums import (
    AccountType,
    BackupStatus,
    BackupType,
    ControlStatus,
    EnvironmentKind,
    EstimatedEffort,
    FindingStatus,
    PluginStatus,
    RemediationPriority,
    RemediationStatus,
    Severity,
    UpdateStatus,
    VerificationStatus,
    VulnerabilityIndicator,
)
from woo_security_simulator.domain.errors import DomainValidationError
from woo_security_simulator.domain.security import (
    BackupRecord,
    Plugin,
    RemediationAction,
    SecurityControl,
    SecurityFinding,
    SiteProfile,
    UserAccount,
)

NOW = datetime(2026, 7, 30, tzinfo=UTC)


def test_site_profile_requires_reserved_url_and_simulation_marker() -> None:
    with pytest.raises(DomainValidationError):
        SiteProfile(
            "site_demo",
            "Store",
            EnvironmentKind.DEMONSTRATION,
            "https://invalid.example",
            "6.8.1",
            "9.9.0",
            "8.3.0",
            True,
            NOW,
            simulated=False,
        )


def test_plugin_update_requires_recommended_version() -> None:
    with pytest.raises(DomainValidationError):
        Plugin(
            "plugin_demo",
            "Demo",
            "demo",
            "1.0.0",
            PluginStatus.ACTIVE,
            UpdateStatus.UPDATE_AVAILABLE,
            date(2026, 1, 1),
            "Fictional",
            VulnerabilityIndicator.REVIEW_RECOMMENDED,
            "Testing.",
        )


def test_administrator_flag_must_match_account_type() -> None:
    with pytest.raises(DomainValidationError):
        UserAccount(
            "user_demo",
            "Demo",
            "demo@example.test",
            AccountType.CUSTOMER,
            True,
            False,
            ControlStatus.PARTIAL,
            NOW,
            True,
        )


def test_failed_control_requires_finding_or_exception() -> None:
    with pytest.raises(DomainValidationError):
        SecurityControl(
            "control_demo",
            "category_demo",
            "Control",
            "Description",
            ControlStatus.FAIL,
            Severity.HIGH,
            "Evidence",
            "Verify",
        )


def make_finding(**overrides: object) -> SecurityFinding:
    values = {
        "id": "finding_demo",
        "title": "Demo finding",
        "category_id": "category_demo",
        "severity": Severity.HIGH,
        "status": FindingStatus.OPEN,
        "affected_component": "plugin_demo",
        "description": "Description",
        "evidence": "Evidence",
        "business_impact": "Impact",
        "recommended_remediation": "Remediation",
        "priority": RemediationPriority.NEXT,
        "estimated_effort": EstimatedEffort.SMALL,
        "before_state": "Before",
        "after_state": None,
        "verification_status": VerificationStatus.NOT_STARTED,
    }
    values.update(overrides)
    return SecurityFinding(**values)  # type: ignore[arg-type]


def test_remediated_finding_requires_after_state_and_verification_state() -> None:
    with pytest.raises(DomainValidationError) as error:
        make_finding(status=FindingStatus.REMEDIATED)
    assert {issue.field for issue in error.value.issues} == {"after_state", "verification_status"}


def test_accepted_finding_requires_reason() -> None:
    with pytest.raises(DomainValidationError):
        make_finding(status=FindingStatus.ACCEPTED)


def test_completed_action_requires_timestamp() -> None:
    with pytest.raises(DomainValidationError):
        RemediationAction(
            "action_demo",
            "finding_demo",
            "Action",
            RemediationPriority.NEXT,
            EstimatedEffort.SMALL,
            RemediationStatus.COMPLETED,
            ("Verify.",),
        )


def test_successful_backup_requires_completion() -> None:
    with pytest.raises(DomainValidationError):
        BackupRecord("backup_demo", NOW, None, BackupType.FULL, BackupStatus.SUCCEEDED, False)
