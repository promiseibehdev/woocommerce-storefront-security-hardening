"""Privacy-safe JSON export for the fictional security demonstration."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from ..errors import ReportError
from ..metadata import (
    APPLICATION_NAME,
    APPLICATION_VERSION,
    FICTIONAL_STORE_NAME,
    SIMULATION_NOTICE,
)
from ..repositories.unit_of_work import UnitOfWork
from ..serialization import to_primitive
from .security import ComparisonService, FindingService, RiskService, SecurityScoringService

PRIVACY_STATEMENT = (
    "This report contains fictional portfolio demonstration data only. It contains no "
    "credentials, payment details, browser data, or real customer information."
)


class SecurityReportService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def generate(self, *, audited_at: datetime) -> str:
        snapshots = self.uow.audit_snapshots.list()
        if not snapshots or self.uow.site_profile is None:
            raise ReportError("security report requires an explicitly loaded fictional audit")
        before = next((item for item in snapshots if item.kind.value == "before"), snapshots[0])
        after = next((item for item in snapshots if item.kind.value == "after"), snapshots[-1])
        score = SecurityScoringService(self.uow).score_snapshot(after)
        comparison = ComparisonService(self.uow).compare(before, after)
        findings = FindingService(self.uow).prioritized()
        risk = RiskService()
        report = {
            "application": {
                "name": APPLICATION_NAME,
                "version": APPLICATION_VERSION,
                "store": FICTIONAL_STORE_NAME,
            },
            "disclaimer": SIMULATION_NOTICE,
            "audit_timestamp": audited_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "site_profile": {
                "site_name": self.uow.site_profile.site_name,
                "environment": self.uow.site_profile.environment.value,
                "wordpress_version": after.site_profile.wordpress_version,
                "woocommerce_version": after.site_profile.woocommerce_version,
                "php_version": after.site_profile.php_version,
                "https_enabled": after.site_profile.https_enabled,
            },
            "score": to_primitive(score),
            "finding_summary": {
                "total": len(findings),
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "severity": item.severity.value,
                        "status": after.finding_states[item.id].value,
                        "business_impact": item.business_impact,
                    }
                    for item in findings
                ],
            },
            "control_summary": {
                "total": self.uow.security_controls.count(),
                "states": {
                    status: sum(value.value == status for value in after.control_states.values())
                    for status in ("pass", "fail", "partial", "not_applicable")
                },
            },
            "plugin_summary": [
                {
                    "id": item.id,
                    "name": item.name,
                    "status": item.status.value,
                    "risk": risk.plugin(item).level.value,
                    "reasons": list(risk.plugin(item).reasons),
                }
                for item in self.uow.plugins.list()
            ],
            "theme_summary": [
                {
                    "id": item.id,
                    "name": item.name,
                    "status": item.status.value,
                    "child_theme": item.is_child_theme,
                }
                for item in self.uow.themes.list()
            ],
            "prioritized_remediation": [
                {
                    "finding_id": item.finding_id,
                    "title": item.title,
                    "priority": item.priority.value,
                    "effort": item.effort.value,
                    "status": item.status.value,
                }
                for item in self.uow.remediation_actions.list()
            ],
            "comparison": to_primitive(comparison),
            "privacy_statement": PRIVACY_STATEMENT,
        }
        encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if "C:\\Users\\" in encoded or "api_key" in encoded.casefold():
            raise ReportError("report privacy validation failed")
        return encoded + "\n"
