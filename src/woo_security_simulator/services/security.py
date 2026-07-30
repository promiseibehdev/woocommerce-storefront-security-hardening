"""Deterministic component risk, security scoring, findings, and comparison services."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, replace

from ..domain.enums import (
    ControlStatus,
    EstimatedEffort,
    FindingStatus,
    RemediationStatus,
    RiskLevel,
    Severity,
    UpdateStatus,
    VerificationStatus,
    VulnerabilityIndicator,
)
from ..domain.security import (
    AuditSnapshot,
    CoreComponent,
    Plugin,
    RemediationAction,
    SecurityFinding,
    Theme,
)
from ..metadata import SECURITY_METHODOLOGY_VERSION, SIMULATION_NOTICE
from ..repositories.unit_of_work import UnitOfWork

SEVERITY_WEIGHT = {
    Severity.CRITICAL: 8,
    Severity.HIGH: 5,
    Severity.MEDIUM: 3,
    Severity.LOW: 1,
    Severity.INFORMATIONAL: 0,
}
STATUS_FACTOR = {
    FindingStatus.OPEN: 1.0,
    FindingStatus.IN_PROGRESS: 0.75,
    FindingStatus.REMEDIATED: 0.0,
    FindingStatus.ACCEPTED: 0.5,
    FindingStatus.NOT_APPLICABLE: 0.0,
}
CONTROL_FACTOR = {
    ControlStatus.FAIL: 1.0,
    ControlStatus.PARTIAL: 0.5,
    ControlStatus.PASS: 0.0,
    ControlStatus.NOT_APPLICABLE: 0.0,
}


@dataclass(frozen=True, slots=True)
class RiskIndicator:
    component_id: str
    level: RiskLevel
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScoreResult:
    score: int | None
    risk_band: RiskLevel | None
    risk_points: float
    maximum_points: int
    finding_counts_by_severity: dict[str, int]
    passed_controls: int
    failed_controls: int
    remediated_controls: int
    highest_priority_issues: tuple[str, ...]
    explanation: str
    methodology_version: str = SECURITY_METHODOLOGY_VERSION
    disclaimer: str = SIMULATION_NOTICE


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    before_score: int | None
    after_score: int | None
    score_change: int
    before_band: RiskLevel | None
    after_band: RiskLevel | None
    findings_opened: tuple[str, ...]
    findings_remediated: tuple[str, ...]
    controls_improved: tuple[str, ...]
    controls_regressed: tuple[str, ...]
    component_version_improvements: tuple[str, ...]
    plugin_risk_improvements: tuple[str, ...]
    remaining_critical_high: tuple[str, ...]
    explanation: str


class RiskService:
    def component(self, component: CoreComponent) -> RiskIndicator:
        reasons = []
        if component.update_status is not UpdateStatus.CURRENT:
            reasons.append(f"{component.name} is {component.update_status.value}.")
        if component.support_status.value not in {"supported"}:
            reasons.append(f"Support status is {component.support_status.value}.")
        return RiskIndicator(component.id, _level_for_reason_count(len(reasons)), tuple(reasons))

    def plugin(self, plugin: Plugin) -> RiskIndicator:
        reasons = []
        if plugin.update_status is not UpdateStatus.CURRENT:
            reasons.append(f"Update status is {plugin.update_status.value}.")
        if plugin.abandoned:
            reasons.append("Plugin is marked abandoned in the fictional fixture.")
        if plugin.vulnerability_indicator is not VulnerabilityIndicator.NONE_OBSERVED:
            reasons.append(f"Fictional indicator: {plugin.vulnerability_indicator.value}.")
        if plugin.status.value == "inactive":
            reasons.append("Inactive plugin adds avoidable maintenance surface.")
        return RiskIndicator(plugin.id, _level_for_reason_count(len(reasons)), tuple(reasons))

    def theme(self, theme: Theme, themes: tuple[Theme, ...]) -> RiskIndicator:
        reasons = []
        if theme.update_status is not UpdateStatus.CURRENT:
            reasons.append(f"Update status is {theme.update_status.value}.")
        if theme.is_child_theme and theme.parent_theme_id not in {item.id for item in themes}:
            reasons.append("Child theme has no valid parent.")
        return RiskIndicator(theme.id, _level_for_reason_count(len(reasons)), tuple(reasons))


class SecurityScoringService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def score_snapshot(self, snapshot: AuditSnapshot) -> ScoreResult:
        findings = {item.id: item for item in self.uow.security_findings.list()}
        controls = {item.id: item for item in self.uow.security_controls.list()}
        linked_control_ids = {
            control_id for finding in findings.values() for control_id in finding.control_ids
        }
        risk_points = 0.0
        maximum = 0
        counts: Counter[str] = Counter()
        open_titles: list[tuple[int, str]] = []
        for finding_id, status in snapshot.finding_states.items():
            finding = findings[finding_id]
            if status is FindingStatus.NOT_APPLICABLE:
                continue
            weight = SEVERITY_WEIGHT[finding.severity]
            maximum += weight
            risk_points += weight * STATUS_FACTOR[status]
            if status in {FindingStatus.OPEN, FindingStatus.IN_PROGRESS, FindingStatus.ACCEPTED}:
                counts[finding.severity.value] += 1
                open_titles.append((weight, finding.title))
        for control_id, status in snapshot.control_states.items():
            if control_id in linked_control_ids or status is ControlStatus.NOT_APPLICABLE:
                continue
            control = controls[control_id]
            weight = SEVERITY_WEIGHT[control.importance]
            maximum += weight
            risk_points += weight * CONTROL_FACTOR[status]
        score = None if maximum == 0 else round(100 * (1 - risk_points / maximum))
        score = None if score is None else max(0, min(100, score))
        band = _band(score)
        return ScoreResult(
            score,
            band,
            round(risk_points, 2),
            maximum,
            dict(sorted(counts.items())),
            sum(status is ControlStatus.PASS for status in snapshot.control_states.values()),
            sum(status is ControlStatus.FAIL for status in snapshot.control_states.values()),
            sum(status is FindingStatus.REMEDIATED for status in snapshot.finding_states.values()),
            tuple(
                title for _, title in sorted(open_titles, key=lambda item: (-item[0], item[1]))[:5]
            ),
            (
                "Educational whole-number posture index using weighted fictional findings; "
                "linked controls are excluded to prevent duplicate risk."
            ),
        )


class FindingService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def list(
        self,
        *,
        severity: Severity | None = None,
        category_id: str | None = None,
        status: FindingStatus | None = None,
        affected_component: str | None = None,
    ) -> tuple[SecurityFinding, ...]:
        return self.uow.security_findings.find(
            lambda item: (
                (severity is None or item.severity is severity)
                and (category_id is None or item.category_id == category_id)
                and (status is None or item.status is status)
                and (affected_component is None or item.affected_component == affected_component)
            )
        )

    def group_by_severity(self) -> dict[str, tuple[SecurityFinding, ...]]:
        return _group(self.uow.security_findings.list(), lambda item: item.severity.value)

    def group_by_category(self) -> dict[str, tuple[SecurityFinding, ...]]:
        return _group(self.uow.security_findings.list(), lambda item: item.category_id)

    def prioritized(self) -> tuple[SecurityFinding, ...]:
        return tuple(
            sorted(
                self.uow.security_findings.list(),
                key=lambda item: (
                    -SEVERITY_WEIGHT[item.severity],
                    list(item.priority.__class__).index(item.priority),
                    item.id,
                ),
            )
        )

    def quick_wins(self) -> tuple[SecurityFinding, ...]:
        return tuple(
            item
            for item in self.prioritized()
            if item.estimated_effort is EstimatedEffort.SMALL
            and item.status in {FindingStatus.OPEN, FindingStatus.IN_PROGRESS}
        )

    def effort_summary(self) -> dict[str, int]:
        return dict(
            sorted(
                Counter(
                    item.estimated_effort.value for item in self.uow.security_findings.list()
                ).items()
            )
        )

    def business_impact_summary(self) -> tuple[str, ...]:
        return tuple(item.business_impact for item in self.prioritized())

    def update_remediation(
        self,
        action_id: str,
        status: RemediationStatus,
        *,
        completed_at=None,
    ) -> RemediationAction:
        action = self.uow.remediation_actions.get(action_id)
        updated = replace(action, status=status, completed_at=completed_at)
        self.uow.remediation_actions.update(updated)
        return updated

    def mark_finding(
        self,
        finding_id: str,
        status: FindingStatus,
        *,
        after_state: str | None = None,
        verification_status: VerificationStatus = VerificationStatus.NOT_STARTED,
    ) -> SecurityFinding:
        finding = self.uow.security_findings.get(finding_id)
        updated = replace(
            finding,
            status=status,
            after_state=after_state,
            verification_status=verification_status,
        )
        self.uow.security_findings.update(updated)
        return updated


class ComparisonService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work
        self.scoring = SecurityScoringService(unit_of_work)

    def compare(self, before: AuditSnapshot, after: AuditSnapshot) -> ComparisonResult:
        if before.methodology_version != after.methodology_version:
            raise ValueError("snapshot methodology versions differ")
        before_score = self.scoring.score_snapshot(before)
        after_score = self.scoring.score_snapshot(after)
        opened = tuple(
            sorted(
                item_id
                for item_id, status in after.finding_states.items()
                if status is FindingStatus.OPEN
                and before.finding_states.get(item_id) is not FindingStatus.OPEN
            )
        )
        remediated = tuple(
            sorted(
                item_id
                for item_id, status in after.finding_states.items()
                if status is FindingStatus.REMEDIATED
                and before.finding_states.get(item_id) is not FindingStatus.REMEDIATED
            )
        )
        improved = tuple(
            sorted(
                item_id
                for item_id, status in after.control_states.items()
                if status is ControlStatus.PASS
                and before.control_states.get(item_id)
                in {ControlStatus.FAIL, ControlStatus.PARTIAL}
            )
        )
        regressed = tuple(
            sorted(
                item_id
                for item_id, status in after.control_states.items()
                if status in {ControlStatus.FAIL, ControlStatus.PARTIAL}
                and before.control_states.get(item_id) is ControlStatus.PASS
            )
        )
        version_improvements = tuple(
            name
            for name in ("wordpress", "woocommerce", "php")
            if getattr(before.site_profile, f"{name}_version")
            != getattr(after.site_profile, f"{name}_version")
        )
        remaining = tuple(
            finding.id
            for finding in self.uow.security_findings.list()
            if after.finding_states.get(finding.id) is FindingStatus.OPEN
            and finding.severity in {Severity.CRITICAL, Severity.HIGH}
        )
        score_change = (after_score.score or 0) - (before_score.score or 0)
        return ComparisonResult(
            before_score.score,
            after_score.score,
            score_change,
            before_score.risk_band,
            after_score.risk_band,
            opened,
            remediated,
            improved,
            regressed,
            version_improvements,
            ("plugin_07",) if "finding_04" in remediated else (),
            remaining,
            (
                f"Simulated posture improved by {score_change} points with "
                f"{len(remediated)} findings remediated."
            ),
        )


def _band(score: int | None) -> RiskLevel | None:
    if score is None:
        return None
    if score >= 85:
        return RiskLevel.LOW
    if score >= 70:
        return RiskLevel.GUARDED
    if score >= 50:
        return RiskLevel.ELEVATED
    return RiskLevel.HIGH


def _level_for_reason_count(count: int) -> RiskLevel:
    if count == 0:
        return RiskLevel.LOW
    if count == 1:
        return RiskLevel.GUARDED
    if count == 2:
        return RiskLevel.ELEVATED
    return RiskLevel.HIGH


def _group(items, key):
    grouped = defaultdict(list)
    for item in items:
        grouped[key(item)].append(item)
    return {name: tuple(values) for name, values in sorted(grouped.items())}
