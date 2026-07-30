# Phase 5 — Security Workspace

## Scope

Phase 5 adds the read-only Security workspace to the existing Streamlit application.
The storefront remains intact. No authentication, live WordPress/WooCommerce connection,
CVE lookup, external dashboard, network request, deployment, GitHub workflow, or
portfolio change is included.

## Navigation

The sidebar now has a clear Storefront/Security workspace switcher. Security contains
exactly five destinations:

1. Security Overview
2. Components
3. Findings
4. Hardening
5. Reports

Both workspaces share the same per-session `ApplicationStateService` and explicit
**Load Fictional Sample Data** action. Security starts empty and never loads the fixture
automatically.

## Application-layer summaries

`SecurityDashboardService` joins immutable snapshot state with existing repositories and
security services. It keeps current-audit filtering, component summaries, quick-win
selection, and completed/remaining remediation outside Streamlit.

It does not replace scoring, comparison, risk, finding, or report logic. Those calculations
continue to use the approved Phase 3 services.

## Overview

The Overview displays:

- overall after score and risk band;
- before score, after score, and improvement;
- remaining critical/high findings;
- passed/failed controls and remediated findings;
- quick-win count;
- scoring explanation and simulator/certification disclaimer.

The deterministic fixture renders **35 / High** before, **83 / Guarded** after, and a
**+48** improvement.

## Components

Core & Runtime, Plugins, and Themes tabs display version, installed/active status, update
state, text-plus-icon risk, lifecycle information, child-theme state, and deterministic
fixture reasons. Plugin filtering supports active, inactive, and abandoned lifecycle
views.

No live version, CVE, or vulnerability service is queried.

## Findings

Findings search covers title, component, category, impact, and remediation. Filters cover
severity, category, and current after-snapshot status. Each result exposes title,
severity, category, affected component, business impact, recommended remediation,
evidence, and current status.

## Hardening

The prioritized plan joins each finding with its remediation action and current
after-snapshot state. It separates quick wins, completed items, and remaining items while
showing severity, priority, effort, business impact, remediation, and verification steps.
The workspace is read-only and never silently marks a finding fixed.

## Reports

Reports displays before/after score and band changes, remediated findings, improved or
regressed controls, component-version changes, plugin-risk improvements, and remaining
critical/high findings.

The existing `SecurityReportService` generates the JSON report in memory. Streamlit
exposes it through a download control; the application does not write it automatically.
The page includes the privacy statement, simulator disclaimer, hosted persistence warning,
and an explicit note that PDF export is not implemented.

## Responsive and accessible presentation

- Shared Streamlit columns and the existing 640px mobile breakpoint support narrow views.
- Status, severity, lifecycle, and risk use readable text in addition to icons.
- Filters have visible labels.
- Findings and hardening details use headings and expandable sections.
- Empty results explain how to recover.
- High-contrast shared styling remains unchanged.
- No essential result is communicated only by color or a chart.

## Phase 6 guidance

Phase 6 may perform quality hardening, accessibility/manual viewport review, performance
profiling, documentation completion, screenshot planning, release checklists, and final
privacy/secrets/version audits. Git initialization, publication, deployment, and portfolio
integration remain reserved for Phase 7 unless explicitly authorized.

