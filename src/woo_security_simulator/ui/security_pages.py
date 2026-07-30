"""Security workspace presentation over existing deterministic services."""

from __future__ import annotations

import json

import streamlit as st

from ..domain.enums import FindingStatus, RiskLevel, Severity
from ..metadata import SIMULATION_NOTICE
from ..services.report import PRIVACY_STATEMENT, SecurityReportService
from ..services.security_dashboard import (
    ComponentSummary,
    HardeningSummary,
    SecurityDashboardService,
)
from .components import empty_state, notice, page_heading
from .state import application_state


def render_security_overview() -> None:
    page_heading(
        "Security Overview",
        "A transparent, fictional WordPress and WooCommerce hardening demonstration.",
    )
    dashboard = SecurityDashboardService(application_state().uow)
    summary = dashboard.overview()
    score_columns = st.columns(3)
    score_columns[0].metric(
        "Overall Security Score",
        f"{summary.after.score}/100",
        f"+{summary.improvement} after hardening",
    )
    score_columns[1].metric(
        "Risk Band",
        _risk_label(summary.after.risk_band),
    )
    score_columns[2].metric("Quick Wins", summary.quick_wins)
    comparison_columns = st.columns(3)
    comparison_columns[0].metric("Before Score", summary.before.score)
    comparison_columns[1].metric("After Score", summary.after.score)
    comparison_columns[2].metric("Improvement", f"+{summary.improvement}")
    finding_columns = st.columns(3)
    finding_columns[0].metric("Critical Findings", summary.critical_findings)
    finding_columns[1].metric("High Findings", summary.high_findings)
    finding_columns[2].metric("Remediated Findings", summary.remediated_findings)
    control_columns = st.columns(3)
    control_columns[0].metric("Passed Controls", summary.passed_controls)
    control_columns[1].metric("Failed Controls", summary.failed_controls)
    control_columns[2].metric(
        "Controls Reviewed",
        summary.passed_controls + summary.failed_controls,
    )
    st.subheader("What changed")
    st.write(summary.explanation)
    st.caption(summary.after.explanation)
    st.warning(
        "Simulator disclaimer: this educational score is not an industry certification, "
        "compliance result, live scan, or guarantee of security."
    )
    notice(SIMULATION_NOTICE)


def render_components() -> None:
    page_heading(
        "Components",
        "Version posture and fictional lifecycle indicators for the simulated environment.",
    )
    summaries = SecurityDashboardService(application_state().uow).components()
    if not summaries:
        empty_state(
            "No component inventory",
            "Load or restore a valid fictional security dataset to review components.",
        )
        return
    core_tab, plugin_tab, theme_tab = st.tabs(("Core & Runtime", "Plugins", "Themes"))
    with core_tab:
        for kind, label in (
            ("wordpress", "WordPress Core"),
            ("woocommerce", "WooCommerce"),
            ("php", "PHP"),
        ):
            component = next((item for item in summaries if item.kind == kind), None)
            if component is None:
                empty_state(
                    f"{label} unavailable",
                    "This fictional component is missing from the current audit state.",
                )
            else:
                _component_card(component, heading=label)
    with plugin_tab:
        plugins = tuple(item for item in summaries if item.kind == "plugin")
        st.write(f"**{len(plugins)} fictional plugins reviewed**")
        lifecycle_filter = st.selectbox(
            "Plugin lifecycle",
            ("All plugins", "Active", "Inactive", "Abandoned"),
        )
        filtered = tuple(
            item
            for item in plugins
            if lifecycle_filter == "All plugins"
            or (lifecycle_filter == "Active" and item.status == "active")
            or (lifecycle_filter == "Inactive" and item.status == "inactive")
            or (lifecycle_filter == "Abandoned" and item.lifecycle == "abandoned")
        )
        for component in filtered:
            _component_card(component)
    with theme_tab:
        for component in (item for item in summaries if item.kind == "theme"):
            _component_card(component)
        st.info(
            "Info: the active Northstar Child fixture demonstrates child-theme separation "
            "from its installed parent theme."
        )
    st.caption(
        "All component and vulnerability indicators are deterministic fictional fixtures. "
        "No CVE service or live WordPress system was queried."
    )


def render_findings() -> None:
    page_heading(
        "Findings",
        "Search and filter actionable fictional security findings.",
    )
    uow = application_state().uow
    dashboard = SecurityDashboardService(uow)
    categories = uow.security_categories.list()
    with st.container(border=True):
        search = st.text_input(
            "Search findings",
            placeholder="Search title, component, category, impact, or remediation",
        )
        first, second, third = st.columns(3)
        severity_value = first.selectbox(
            "Severity",
            ("All severities", *(item.value for item in Severity)),
            format_func=_humanize,
        )
        category_value = second.selectbox(
            "Category",
            ("All categories", *(item.id for item in categories)),
            format_func=lambda value: (
                value if value == "All categories" else uow.security_categories.get(value).name
            ),
        )
        status_value = third.selectbox(
            "Status",
            ("All statuses", *(item.value for item in FindingStatus)),
            format_func=_humanize,
        )
    findings = dashboard.findings(
        search=search,
        severity=None if severity_value == "All severities" else Severity(severity_value),
        category_id=None if category_value == "All categories" else category_value,
        status=None if status_value == "All statuses" else FindingStatus(status_value),
    )
    st.write(f"**{len(findings)} findings shown**")
    if not findings:
        empty_state("No matching findings", "Clear or broaden the security filters.")
        return
    for summary in findings:
        finding = summary.finding
        with st.expander(
            f"{_severity_icon(finding.severity)} {finding.severity.value.title()} · {finding.title}"
        ):
            columns = st.columns(3)
            columns[0].markdown(f"**Category**  \n{summary.category_name}")
            columns[1].markdown(f"**Component**  \n{finding.affected_component}")
            columns[2].markdown(
                f"**Current status**  \n{_status_icon(summary.current_status)} "
                f"{_humanize(summary.current_status.value)}"
            )
            st.markdown(f"**Business impact**  \n{finding.business_impact}")
            st.markdown(f"**Recommended remediation**  \n{finding.recommended_remediation}")
            st.caption(f"Evidence: {finding.evidence}")


def render_hardening() -> None:
    page_heading(
        "Hardening",
        "Prioritized remediation plan based on the fictional after-audit state.",
    )
    dashboard = SecurityDashboardService(application_state().uow)
    plan = dashboard.hardening_plan()
    quick_wins = dashboard.quick_wins()
    completed = tuple(item for item in plan if item.completed)
    remaining = tuple(item for item in plan if not item.completed)
    metrics = st.columns(4)
    metrics[0].metric("Plan Items", len(plan))
    metrics[1].metric("Quick Wins", len(quick_wins))
    metrics[2].metric("Completed", len(completed))
    metrics[3].metric("Remaining", len(remaining))
    plan_tab, quick_tab, completed_tab, remaining_tab = st.tabs(
        ("Prioritized Plan", "Quick Wins", "Completed", "Remaining")
    )
    with plan_tab:
        _hardening_list(plan)
    with quick_tab:
        _hardening_list(quick_wins)
    with completed_tab:
        _hardening_list(completed)
    with remaining_tab:
        _hardening_list(remaining)
    st.info(
        "Info: completion reflects the immutable fictional after snapshot. "
        "No finding is changed automatically from this read-only workspace."
    )


def render_reports() -> None:
    page_heading(
        "Reports",
        "Compare fictional audits and export a privacy-safe JSON security report.",
    )
    uow = application_state().uow
    dashboard = SecurityDashboardService(uow)
    comparison = dashboard.comparison()
    before, after = dashboard.snapshots()
    metrics = st.columns(4)
    metrics[0].metric("Before", comparison.before_score)
    metrics[1].metric("After", comparison.after_score)
    metrics[2].metric("Score Change", f"+{comparison.score_change}")
    metrics[3].metric(
        "Risk Band Change",
        f"{_risk_label(comparison.before_band)} → {_risk_label(comparison.after_band)}",
    )
    improved, remaining = st.columns(2)
    with improved, st.container(border=True):
        st.subheader("Improvements")
        st.write(f"✓ {len(comparison.findings_remediated)} findings remediated")
        st.write(f"✓ {len(comparison.controls_improved)} controls improved")
        st.write(f"✓ Component versions: {', '.join(comparison.component_version_improvements)}")
        st.write(f"✓ Plugin-risk improvements: {len(comparison.plugin_risk_improvements)}")
    with remaining, st.container(border=True):
        st.subheader("Remaining risk")
        st.write(f"⚠ {len(comparison.remaining_critical_high)} critical/high findings remain")
        st.write(f"⚠ {len(comparison.controls_regressed)} controls regressed")
        st.caption(comparison.explanation)
    report = SecurityReportService(uow).generate(audited_at=after.captured_at)
    parsed = json.loads(report)
    st.download_button(
        "Download fictional security report (JSON)",
        data=report,
        file_name="northstar-fictional-security-report.json",
        mime="application/json",
        use_container_width=True,
    )
    with st.expander("Preview report summary"):
        st.json(
            {
                "application": parsed["application"],
                "score": parsed["score"],
                "control_summary": parsed["control_summary"],
                "privacy_statement": parsed["privacy_statement"],
            }
        )
    st.subheader("Privacy statement")
    st.write(PRIVACY_STATEMENT)
    st.warning(
        "Hosted persistence warning: a future Streamlit Community Cloud filesystem may "
        "reset at any time. This report is generated in memory and is not stored automatically."
    )
    notice(SIMULATION_NOTICE)
    st.caption(
        f"Comparison: {before.label} ({before.captured_at.date()}) to "
        f"{after.label} ({after.captured_at.date()}). PDF export is not implemented."
    )


SECURITY_PAGES = {
    "Security Overview": render_security_overview,
    "Components": render_components,
    "Findings": render_findings,
    "Hardening": render_hardening,
    "Reports": render_reports,
}


def _component_card(component: ComponentSummary, *, heading: str | None = None) -> None:
    with st.container(border=True):
        title, risk = st.columns([3, 1])
        title.markdown(f"### {heading or component.name}")
        risk.markdown(
            f"**{_risk_icon(component.risk.level)} {_risk_label(component.risk.level)} risk**"
        )
        columns = st.columns(4)
        columns[0].markdown(f"**Version**  \n{component.version}")
        columns[1].markdown(f"**Status**  \n{_humanize(component.status)}")
        columns[2].markdown(f"**Update state**  \n{_humanize(component.update_state)}")
        columns[3].markdown(
            f"**Lifecycle**  \n{_humanize(component.lifecycle or 'not applicable')}"
        )
        if component.child_theme is not None:
            st.write(
                f"{'✓' if component.child_theme else '○'} Child-theme status: "
                f"{'Child theme' if component.child_theme else 'Parent/base theme'}"
            )
        if component.risk.reasons:
            for reason in component.risk.reasons:
                st.caption(f"Risk indicator: {reason}")
        else:
            st.caption("No elevated fictional risk indicator for this component.")


def _hardening_list(items: tuple[HardeningSummary, ...]) -> None:
    if not items:
        empty_state("No items", "No remediation items match this view.")
        return
    for item in items:
        with st.expander(
            f"{'✓' if item.completed else '⚠'} {item.finding.title} · "
            f"{item.finding.priority.value.title()}"
        ):
            columns = st.columns(3)
            columns[0].markdown(
                f"**Severity**  \n{_severity_icon(item.finding.severity)} "
                f"{item.finding.severity.value.title()}"
            )
            columns[1].markdown(
                f"**Estimated effort**  \n{_humanize(item.finding.estimated_effort.value)}"
            )
            columns[2].markdown(
                f"**Current status**  \n{_status_icon(item.current_status)} "
                f"{_humanize(item.current_status.value)}"
            )
            st.markdown(f"**Business impact**  \n{item.finding.business_impact}")
            st.markdown(f"**Remediation**  \n{item.finding.recommended_remediation}")
            st.caption("Verification: " + " · ".join(item.action.verification_steps))


def _humanize(value: str) -> str:
    return value.replace("_", " ").title()


def _risk_label(value: RiskLevel | None) -> str:
    return "Not scored" if value is None else value.value.title()


def _risk_icon(value: RiskLevel) -> str:
    return {
        RiskLevel.LOW: "✓",
        RiskLevel.GUARDED: "i",
        RiskLevel.ELEVATED: "⚠",
        RiskLevel.HIGH: "!",
    }[value]


def _severity_icon(value: Severity) -> str:
    return {
        Severity.CRITICAL: "!",
        Severity.HIGH: "▲",
        Severity.MEDIUM: "⚠",
        Severity.LOW: "i",
        Severity.INFORMATIONAL: "○",
    }[value]


def _status_icon(value: FindingStatus) -> str:
    return {
        FindingStatus.OPEN: "!",
        FindingStatus.IN_PROGRESS: "…",
        FindingStatus.REMEDIATED: "✓",
        FindingStatus.ACCEPTED: "i",
        FindingStatus.NOT_APPLICABLE: "○",
    }[value]
