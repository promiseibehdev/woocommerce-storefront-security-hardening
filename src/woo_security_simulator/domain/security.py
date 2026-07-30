"""Security-audit domain models for fictional educational data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from types import MappingProxyType

from .enums import (
    AccountType,
    ActivityEventType,
    ActivityOutcome,
    BackupStatus,
    BackupType,
    ControlStatus,
    CoreComponentType,
    EnvironmentKind,
    EstimatedEffort,
    FindingStatus,
    PluginStatus,
    RemediationPriority,
    RemediationStatus,
    RiskLevel,
    Severity,
    SnapshotKind,
    SupportStatus,
    ThemeStatus,
    UpdateStatus,
    VerificationStatus,
    VulnerabilityIndicator,
)
from .validation import (
    Validator,
    duplicates,
    is_fictional_email,
    is_reserved_test_url,
    is_utc_aware,
    is_valid_slug,
    is_valid_version,
    safe_metadata,
)


@dataclass(frozen=True, slots=True)
class SiteProfile:
    id: str
    site_name: str
    environment: EnvironmentKind
    base_url_label: str
    wordpress_version: str
    woocommerce_version: str
    php_version: str
    https_enabled: bool
    captured_at: datetime
    simulated: bool = True
    notes: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.site_name, "site_name", maximum=120)
        validator.require(
            is_reserved_test_url(self.base_url_label),
            "base_url_label",
            "must use a reserved .test hostname",
        )
        for field_name in ("wordpress_version", "woocommerce_version", "php_version"):
            validator.require(
                is_valid_version(getattr(self, field_name)),
                field_name,
                "must be a version-like value",
            )
        validator.require(is_utc_aware(self.captured_at), "captured_at", "must be timezone-aware")
        validator.require(
            self.simulated, "simulated", "must explicitly mark the profile as simulated"
        )
        if self.notes is not None:
            validator.text(self.notes, "notes", maximum=1000)
        validator.finish()


@dataclass(frozen=True, slots=True)
class CoreComponent:
    id: str
    name: str
    component_type: CoreComponentType
    installed_version: str
    recommended_version: str
    update_status: UpdateStatus
    support_status: SupportStatus
    end_of_support_date: date | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=100)
        validator.require(
            is_valid_version(self.installed_version), "installed_version", "is invalid"
        )
        validator.require(
            is_valid_version(self.recommended_version), "recommended_version", "is invalid"
        )
        validator.require(
            self.update_status is not UpdateStatus.CURRENT
            or self.installed_version == self.recommended_version,
            "update_status",
            "current requires matching installed and recommended versions",
        )
        validator.finish()


@dataclass(frozen=True, slots=True)
class Plugin:
    id: str
    name: str
    slug: str
    version: str
    status: PluginStatus
    update_status: UpdateStatus
    last_updated_on: date
    publisher: str
    vulnerability_indicator: VulnerabilityIndicator
    business_purpose: str
    recommended_version: str | None = None
    abandoned: bool = False
    known_issue_summary: str | None = None
    replacement_candidate: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=120)
        validator.require(is_valid_slug(self.slug), "slug", "must be a lowercase URL-safe slug")
        validator.require(is_valid_version(self.version), "version", "is invalid")
        validator.text(self.publisher, "publisher", maximum=120)
        validator.text(self.business_purpose, "business_purpose", maximum=500)
        if self.recommended_version is not None:
            validator.require(
                is_valid_version(self.recommended_version), "recommended_version", "is invalid"
            )
        validator.require(
            self.update_status is not UpdateStatus.UPDATE_AVAILABLE
            or self.recommended_version is not None,
            "recommended_version",
            "is required when an update is available",
        )
        if self.known_issue_summary is not None:
            validator.text(self.known_issue_summary, "known_issue_summary", maximum=1000)
        if self.replacement_candidate is not None:
            validator.text(self.replacement_candidate, "replacement_candidate", maximum=120)
        validator.finish()


@dataclass(frozen=True, slots=True)
class Theme:
    id: str
    name: str
    version: str
    status: ThemeStatus
    update_status: UpdateStatus
    is_child_theme: bool
    parent_theme_id: str | None = None
    recommended_version: str | None = None
    last_updated_on: date | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=120)
        validator.require(is_valid_version(self.version), "version", "is invalid")
        validator.require(
            not self.is_child_theme or self.parent_theme_id is not None,
            "parent_theme_id",
            "is required for a child theme",
        )
        if self.parent_theme_id is not None:
            validator.identifier(self.parent_theme_id, "parent_theme_id")
            validator.require(
                self.parent_theme_id != self.id, "parent_theme_id", "cannot reference itself"
            )
        if self.recommended_version is not None:
            validator.require(
                is_valid_version(self.recommended_version), "recommended_version", "is invalid"
            )
        validator.require(
            self.update_status is not UpdateStatus.UPDATE_AVAILABLE
            or self.recommended_version is not None,
            "recommended_version",
            "is required when an update is available",
        )
        validator.finish()


@dataclass(frozen=True, slots=True)
class UserAccount:
    id: str
    display_name: str
    email: str
    account_type: AccountType
    is_administrator: bool
    two_factor_enabled: bool
    password_policy_status: ControlStatus
    last_login_at: datetime
    active: bool
    notes: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.display_name, "display_name", maximum=100)
        validator.require(
            is_fictional_email(self.email), "email", "must use the example.test domain"
        )
        validator.require(
            is_utc_aware(self.last_login_at), "last_login_at", "must be timezone-aware"
        )
        validator.require(
            self.is_administrator == (self.account_type is AccountType.ADMINISTRATOR),
            "is_administrator",
            "must agree with account_type",
        )
        if self.notes is not None:
            validator.text(self.notes, "notes", maximum=1000)
        validator.finish()


@dataclass(frozen=True, slots=True)
class SecurityCategory:
    id: str
    name: str
    description: str
    display_order: int

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=120)
        validator.text(self.description, "description", maximum=1000)
        validator.require(self.display_order >= 0, "display_order", "must be nonnegative")
        validator.finish()


@dataclass(frozen=True, slots=True)
class SecurityControl:
    id: str
    category_id: str
    title: str
    description: str
    status: ControlStatus
    importance: Severity
    evidence_summary: str
    verification_guidance: str
    related_component_id: str | None = None
    finding_id: str | None = None
    exception_reason: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.identifier(self.category_id, "category_id")
        validator.text(self.title, "title", maximum=180)
        validator.text(self.description, "description", maximum=1500)
        validator.text(self.evidence_summary, "evidence_summary", maximum=1500)
        validator.text(self.verification_guidance, "verification_guidance", maximum=1500)
        if self.related_component_id is not None:
            validator.identifier(self.related_component_id, "related_component_id")
        if self.finding_id is not None:
            validator.identifier(self.finding_id, "finding_id")
        if self.exception_reason is not None:
            validator.text(self.exception_reason, "exception_reason", maximum=1000)
        validator.require(
            self.status not in {ControlStatus.FAIL, ControlStatus.PARTIAL}
            or self.finding_id is not None
            or self.exception_reason is not None,
            "finding_id",
            "a failed or partial control requires a finding or exception reason",
        )
        validator.finish()


@dataclass(frozen=True, slots=True)
class SecurityFinding:
    id: str
    title: str
    category_id: str
    severity: Severity
    status: FindingStatus
    affected_component: str
    description: str
    evidence: str
    business_impact: str
    recommended_remediation: str
    priority: RemediationPriority
    estimated_effort: EstimatedEffort
    before_state: str
    after_state: str | None
    verification_status: VerificationStatus
    control_ids: tuple[str, ...] = ()
    owner_label: str | None = None
    target_phase: str | None = None
    accepted_risk_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "control_ids", tuple(self.control_ids))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.identifier(self.category_id, "category_id")
        for field_name, maximum in (
            ("title", 180),
            ("affected_component", 180),
            ("description", 2000),
            ("evidence", 2000),
            ("business_impact", 1500),
            ("recommended_remediation", 2000),
            ("before_state", 1500),
        ):
            validator.text(getattr(self, field_name), field_name, maximum=maximum)
        if self.after_state is not None:
            validator.text(self.after_state, "after_state", maximum=1500)
        for control_id in self.control_ids:
            validator.identifier(control_id, "control_ids")
        validator.require(
            not duplicates(self.control_ids), "control_ids", "must not contain duplicates"
        )
        validator.require(
            self.status is not FindingStatus.REMEDIATED or self.after_state is not None,
            "after_state",
            "is required for a remediated finding",
        )
        validator.require(
            self.status is not FindingStatus.REMEDIATED
            or self.verification_status
            in {VerificationStatus.PENDING, VerificationStatus.VERIFIED},
            "verification_status",
            "remediated findings must be pending or verified",
        )
        validator.require(
            self.status is not FindingStatus.ACCEPTED or bool(self.accepted_risk_reason),
            "accepted_risk_reason",
            "is required for accepted risk",
        )
        if self.owner_label is not None:
            validator.text(self.owner_label, "owner_label", maximum=100)
        if self.target_phase is not None:
            validator.text(self.target_phase, "target_phase", maximum=80)
        if self.accepted_risk_reason is not None:
            validator.text(self.accepted_risk_reason, "accepted_risk_reason", maximum=1000)
        validator.finish()


@dataclass(frozen=True, slots=True)
class RemediationAction:
    id: str
    finding_id: str
    title: str
    priority: RemediationPriority
    effort: EstimatedEffort
    status: RemediationStatus
    verification_steps: tuple[str, ...]
    owner_label: str | None = None
    due_label: str | None = None
    completed_at: datetime | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "verification_steps", tuple(self.verification_steps))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.identifier(self.finding_id, "finding_id")
        validator.text(self.title, "title", maximum=180)
        validator.require(bool(self.verification_steps), "verification_steps", "must not be empty")
        for step in self.verification_steps:
            validator.text(step, "verification_steps", maximum=500)
        validator.require(
            self.status is not RemediationStatus.COMPLETED or self.completed_at is not None,
            "completed_at",
            "is required for a completed action",
        )
        if self.completed_at is not None:
            validator.require(
                is_utc_aware(self.completed_at), "completed_at", "must be timezone-aware"
            )
        for field_name in ("owner_label", "due_label", "notes"):
            value = getattr(self, field_name)
            if value is not None:
                validator.text(value, field_name, maximum=1000)
        validator.finish()


@dataclass(frozen=True, slots=True)
class ScanSummary:
    snapshot_id: str
    open_counts_by_severity: dict[str, int]
    control_counts_by_status: dict[str, int]
    risk_points: int
    maximum_applicable_points: int
    score_band: RiskLevel
    generated_at: datetime
    methodology_version: str
    simulation_notice: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "open_counts_by_severity", MappingProxyType(dict(self.open_counts_by_severity))
        )
        object.__setattr__(
            self, "control_counts_by_status", MappingProxyType(dict(self.control_counts_by_status))
        )
        validator = Validator(type(self).__name__)
        validator.identifier(self.snapshot_id, "snapshot_id")
        validator.require(
            all(value >= 0 for value in self.open_counts_by_severity.values()),
            "open_counts_by_severity",
            "counts must be nonnegative",
        )
        validator.require(
            all(value >= 0 for value in self.control_counts_by_status.values()),
            "control_counts_by_status",
            "counts must be nonnegative",
        )
        validator.require(self.risk_points >= 0, "risk_points", "must be nonnegative")
        validator.require(
            self.maximum_applicable_points > 0,
            "maximum_applicable_points",
            "must be positive for a scored summary",
        )
        validator.require(
            self.risk_points <= self.maximum_applicable_points,
            "risk_points",
            "cannot exceed maximum_applicable_points",
        )
        validator.require(is_utc_aware(self.generated_at), "generated_at", "must be timezone-aware")
        validator.text(self.methodology_version, "methodology_version", maximum=30)
        validator.text(self.simulation_notice, "simulation_notice", maximum=500)
        validator.require(
            "simulat" in self.simulation_notice.casefold(),
            "simulation_notice",
            "must state simulation",
        )
        validator.finish()


@dataclass(frozen=True, slots=True)
class AuditSnapshot:
    id: str
    label: str
    kind: SnapshotKind
    captured_at: datetime
    site_profile: SiteProfile
    component_refs: tuple[str, ...]
    control_states: dict[str, ControlStatus]
    finding_states: dict[str, FindingStatus]
    methodology_version: str
    notes: str | None = None
    previous_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "component_refs", tuple(self.component_refs))
        object.__setattr__(self, "control_states", MappingProxyType(dict(self.control_states)))
        object.__setattr__(self, "finding_states", MappingProxyType(dict(self.finding_states)))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.label, "label", maximum=120)
        validator.require(is_utc_aware(self.captured_at), "captured_at", "must be timezone-aware")
        validator.require(
            not duplicates(self.component_refs), "component_refs", "must not contain duplicates"
        )
        for component_id in self.component_refs:
            validator.identifier(component_id, "component_refs")
        for item_id in (*self.control_states.keys(), *self.finding_states.keys()):
            validator.identifier(item_id, "state id")
        validator.text(self.methodology_version, "methodology_version", maximum=30)
        if self.notes is not None:
            validator.text(self.notes, "notes", maximum=1000)
        if self.previous_snapshot_id is not None:
            validator.identifier(self.previous_snapshot_id, "previous_snapshot_id")
            validator.require(
                self.previous_snapshot_id != self.id,
                "previous_snapshot_id",
                "cannot reference itself",
            )
        validator.finish()


@dataclass(frozen=True, slots=True)
class BackupRecord:
    id: str
    started_at: datetime
    completed_at: datetime | None
    backup_type: BackupType
    status: BackupStatus
    restore_tested: bool
    retention_days: int | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.require(is_utc_aware(self.started_at), "started_at", "must be timezone-aware")
        if self.completed_at is not None:
            validator.require(
                is_utc_aware(self.completed_at), "completed_at", "must be timezone-aware"
            )
            validator.require(
                self.started_at <= self.completed_at, "completed_at", "cannot precede started_at"
            )
        validator.require(
            self.status is not BackupStatus.SUCCEEDED or self.completed_at is not None,
            "completed_at",
            "is required for a successful backup",
        )
        if self.retention_days is not None:
            validator.require(self.retention_days >= 0, "retention_days", "must be nonnegative")
        if self.notes is not None:
            validator.text(self.notes, "notes", maximum=1000)
        validator.finish()


@dataclass(frozen=True, slots=True)
class ActivityEvent:
    id: str
    occurred_at: datetime
    actor_label: str
    event_type: ActivityEventType
    summary: str
    outcome: ActivityOutcome
    component_ref: str | None = None
    metadata: dict[str, str | int | float | bool | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.require(is_utc_aware(self.occurred_at), "occurred_at", "must be timezone-aware")
        validator.text(self.actor_label, "actor_label", maximum=100)
        validator.text(self.summary, "summary", maximum=1000)
        if self.component_ref is not None:
            validator.identifier(self.component_ref, "component_ref")
        validator.require(
            safe_metadata(self.metadata), "metadata", "contains a forbidden or complex value"
        )
        validator.finish()


SecurityModel = (
    SiteProfile
    | CoreComponent
    | Plugin
    | Theme
    | UserAccount
    | SecurityCategory
    | SecurityControl
    | SecurityFinding
    | RemediationAction
    | ScanSummary
    | AuditSnapshot
    | BackupRecord
    | ActivityEvent
)
