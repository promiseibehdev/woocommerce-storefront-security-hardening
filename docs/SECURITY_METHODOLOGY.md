# Security Methodology

## Purpose

The **Simulated Security Posture Score** is an educational portfolio index for the
fictional Northstar Desk & Living fixture. It is not a certification, compliance result,
CVSS calculation, penetration test, vulnerability scan, guarantee, or prediction of
compromise.

No real WordPress/WooCommerce instance or CVE database is connected.

## Finding weights

| Severity | Weight |
|---|---:|
| Critical | 8 |
| High | 5 |
| Medium | 3 |
| Low | 1 |
| Informational | 0 |

Finding status factors:

- Open: 1.00
- In progress: 0.75
- Remediated in the verified snapshot: 0.00
- Accepted risk: 0.50
- Not applicable: excluded

Control factors:

- Fail: 1.00
- Partial: 0.50
- Pass: 0.00
- Not applicable: excluded

## Duplicate-risk prevention

A failed/partial control linked to a finding is represented by the finding points only.
It is excluded from separate control risk. Applicable unlinked controls remain in the
maximum possible points, including when they pass.

## Score and bands

```text
score = round(100 × (1 - risk_points / maximum_applicable_points))
```

No applicable checks produces “Not scored,” not 100.

- 85–100: Low
- 70–84: Guarded
- 50–69: Elevated
- 0–49: High

The UI shows a whole number, band, and underlying counts to avoid fake precision.

## Before and after

Immutable snapshots use the same methodology version. The deterministic fixture scores:

- Before: 35 / High
- After: 83 / Guarded
- Improvement: +48

Comparison identifies opened/remediated findings, improved/regressed controls, version
changes, plugin-risk improvements, and remaining critical/high findings.

## Fictional component indicators

Core/runtime posture uses fixture version/update/support statuses. Plugin posture uses
fixture active/inactive, update, abandonment, and fictional vulnerability indicators.
Theme posture uses update and child/parent relationships. These values do not claim a
publisher, advisory, CVE, or live source was checked.

## Remediation and quick wins

Priority, severity, estimated effort, and the current after-snapshot state determine
presentation order. A quick win is remaining work with small estimated effort and a
todo/in-progress action. The workspace never silently marks a finding fixed.

## Limitations

- Educational fixture data only.
- No threat modeling for a specific real organization.
- No legal, regulatory, privacy, PCI DSS, or professional audit opinion.
- No live configuration, malware, header, file-permission, account, or payment test.
- Score changes explain model state, not real risk reduction.

