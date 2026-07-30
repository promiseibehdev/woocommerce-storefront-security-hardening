"""Read models for the Security workspace; no Streamlit dependency."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.enums import (
    ControlStatus,
    EstimatedEffort,
    FindingStatus,
    RemediationStatus,
    Severity,
)
from ..domain.security import (
    AuditSnapshot,
    CoreComponent,
    Plugin,
    RemediationAction,
    SecurityFinding,
    Theme,
)
from ..repositories.unit_of_work import UnitOfWork
from ..utilities import normalize_search_text
from .security import (
    ComparisonResult,
    ComparisonService,
    RiskIndicator,
    RiskService,
    ScoreResult,
    SecurityScoringService,
)


@dataclass(frozen=True, slots=True)
class OverviewSummary:
    before: ScoreResult
    after: ScoreResult
    improvement: int
    critical_findings: int
    high_findings: int
    passed_controls: int
    failed_controls: int
    remediated_findings: int
    quick_wins: int
    explanation: str


@dataclass(frozen=True, slots=True)
class ComponentSummary:
    id: str
    name: str
    kind: str
    version: str
    status: str
    update_state: str
    risk: RiskIndicator
    child_theme: bool | None = None
    lifecycle: str | None = None


@dataclass(frozen=True, slots=True)
class FindingSummary:
    finding: SecurityFinding
    category_name: str
    current_status: FindingStatus


@dataclass(frozen=True, slots=True)
class HardeningSummary:
    finding: SecurityFinding
    action: RemediationAction
    current_status: FindingStatus
    completed: bool


class SecurityDashboardService:
    """Build deterministic security presentation summaries from repositories/services."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work
        self.scoring = SecurityScoringService(unit_of_work)
        self.risk = RiskService()

    def snapshots(self) -> tuple[AuditSnapshot, AuditSnapshot]:
        before = self.uow.audit_snapshots.get("snapshot_before")
        after = self.uow.audit_snapshots.get("snapshot_after")
        return before, after

    def overview(self) -> OverviewSummary:
        before_snapshot, after_snapshot = self.snapshots()
        before = self.scoring.score_snapshot(before_snapshot)
        after = self.scoring.score_snapshot(after_snapshot)
        active = self.findings()
        quick_wins = self.quick_wins()
        return OverviewSummary(
            before,
            after,
            (after.score or 0) - (before.score or 0),
            sum(
                item.finding.severity is Severity.CRITICAL
                and item.current_status is not FindingStatus.REMEDIATED
                for item in active
            ),
            sum(
                item.finding.severity is Severity.HIGH
                and item.current_status is not FindingStatus.REMEDIATED
                for item in active
            ),
            sum(status is ControlStatus.PASS for status in after_snapshot.control_states.values()),
            sum(status is ControlStatus.FAIL for status in after_snapshot.control_states.values()),
            sum(
                status is FindingStatus.REMEDIATED
                for status in after_snapshot.finding_states.values()
            ),
            len(quick_wins),
            (
                "The after snapshot reflects prioritized fictional hardening. "
                "Linked controls are excluded from duplicate risk calculations."
            ),
        )

    def components(self) -> tuple[ComponentSummary, ...]:
        summaries: list[ComponentSummary] = []
        for component in self.uow.core_components.list():
            summaries.append(self._core_summary(component))
        for plugin in self.uow.plugins.list():
            summaries.append(self._plugin_summary(plugin))
        themes = self.uow.themes.list()
        for theme in themes:
            summaries.append(self._theme_summary(theme, themes))
        return tuple(summaries)

    def findings(
        self,
        *,
        search: str = "",
        severity: Severity | None = None,
        category_id: str | None = None,
        status: FindingStatus | None = None,
    ) -> tuple[FindingSummary, ...]:
        _, after = self.snapshots()
        categories = {item.id: item.name for item in self.uow.security_categories.list()}
        query = normalize_search_text(search)
        summaries = []
        for finding in self.uow.security_findings.list():
            current_status = after.finding_states[finding.id]
            category_name = categories[finding.category_id]
            haystack = normalize_search_text(
                " ".join(
                    (
                        finding.title,
                        finding.affected_component,
                        finding.business_impact,
                        finding.recommended_remediation,
                        category_name,
                    )
                )
            )
            if query and query not in haystack:
                continue
            if severity is not None and finding.severity is not severity:
                continue
            if category_id is not None and finding.category_id != category_id:
                continue
            if status is not None and current_status is not status:
                continue
            summaries.append(FindingSummary(finding, category_name, current_status))
        return tuple(
            sorted(
                summaries,
                key=lambda item: (
                    -_severity_weight(item.finding.severity),
                    item.finding.id,
                ),
            )
        )

    def hardening_plan(self) -> tuple[HardeningSummary, ...]:
        _, after = self.snapshots()
        actions = {item.finding_id: item for item in self.uow.remediation_actions.list()}
        values = tuple(
            HardeningSummary(
                finding,
                actions[finding.id],
                after.finding_states[finding.id],
                after.finding_states[finding.id] is FindingStatus.REMEDIATED,
            )
            for finding in self.uow.security_findings.list()
        )
        return tuple(
            sorted(
                values,
                key=lambda item: (
                    item.completed,
                    -_severity_weight(item.finding.severity),
                    item.finding.id,
                ),
            )
        )

    def quick_wins(self) -> tuple[HardeningSummary, ...]:
        return tuple(
            item
            for item in self.hardening_plan()
            if not item.completed
            and item.finding.estimated_effort is EstimatedEffort.SMALL
            and item.action.status in {RemediationStatus.TODO, RemediationStatus.IN_PROGRESS}
        )

    def comparison(self) -> ComparisonResult:
        return ComparisonService(self.uow).compare(*self.snapshots())

    def _core_summary(self, component: CoreComponent) -> ComponentSummary:
        return ComponentSummary(
            component.id,
            component.name,
            component.component_type.value,
            component.installed_version,
            component.support_status.value,
            component.update_status.value,
            self.risk.component(component),
            lifecycle=component.support_status.value,
        )

    def _plugin_summary(self, plugin: Plugin) -> ComponentSummary:
        lifecycle = "abandoned" if plugin.abandoned else "maintained fixture"
        return ComponentSummary(
            plugin.id,
            plugin.name,
            "plugin",
            plugin.version,
            plugin.status.value,
            plugin.update_status.value,
            self.risk.plugin(plugin),
            lifecycle=lifecycle,
        )

    def _theme_summary(
        self,
        theme: Theme,
        themes: tuple[Theme, ...],
    ) -> ComponentSummary:
        return ComponentSummary(
            theme.id,
            theme.name,
            "theme",
            theme.version,
            theme.status.value,
            theme.update_status.value,
            self.risk.theme(theme, themes),
            child_theme=theme.is_child_theme,
            lifecycle="child theme" if theme.is_child_theme else "parent theme",
        )


def _severity_weight(severity: Severity) -> int:
    return {
        Severity.CRITICAL: 8,
        Severity.HIGH: 5,
        Severity.MEDIUM: 3,
        Severity.LOW: 1,
        Severity.INFORMATIONAL: 0,
    }[severity]
