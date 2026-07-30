# Phase 3 — Data, Storage, Repositories, and Services

## Scope

Phase 3 implements data and business logic only. It does not include Streamlit, `app.py`,
authentication, real commerce, live security scanning, networking, deployment, or
portfolio integration.

## Fictional dataset

`build_sample_state()` creates the deterministic Northstar Desk & Living fixture only
when explicitly called. It contains 20 products, 6 categories, 4 customers, 8 orders,
11 plugins, 22 controls, 14 findings, before/after snapshots, 5 backup-history records,
and 12 activity records. All identities use reserved fictional domains and all images
are local relative references.

The integrity validator checks uniqueness, references, order totals, theme/snapshot/
finding/remediation relationships, fictional identity domains, image paths, and
credential-like content. A broken aggregate fails before save.

## Storage format

The JSON envelope contains:

```text
schema_version
application
version
saved_at
payload
```

Schema version remains 1. The payload uses the Phase 2 serializer, so enums, Decimal
money, UTC timestamps, dates, nested dataclasses, tuples, and mappings reconstruct
without a competing codec.

`JsonStateStore` creates nothing during construction. An explicit save validates the
complete aggregate, writes UTF-8 JSON to a temporary file in the destination directory,
flushes, calls `fsync`, and uses `os.replace`. Temporary files are removed on failure.
Missing, empty, malformed, foreign-application, future-schema, and invalid-model data
raise application-specific errors without silently resetting or overwriting the source.

## Backups and recovery

Saving over an existing valid file first creates a timestamped validated backup. Backup
retention is configurable and deterministic. Listing is newest-first. Restore accepts
only a file inside the managed backup directory and validates it before replacement.
A valid current destination is backed up; a corrupt current destination is preserved
under a timestamped `.corrupt` filename. Restore is always explicit.

The migration registry is intentionally empty because schema 1 needs no migration.
Future schema versions fail safely. A future migration must be an explicit, tested
version-to-version function.

## Repositories and state

`InMemoryRepository` provides deterministic list/get/find/search/add/update/delete/
replace/count/exists operations with conflict and not-found errors. Each `UnitOfWork`
owns private repositories; there is no global or process-wide user state. Immutable
domain records and tuple results prevent callers from mutating repository collections.

`ApplicationStateService` starts empty and coordinates explicit sample loading, save,
load, backup, restore, and empty reset. Constructing it does not create storage or load
fixtures.

## Commerce services

- Catalogue: visible listing, case-insensitive search, combined filters, stable sorting,
  related items, availability, and summary counts.
- Cart: add/increase/decrease/set/remove/clear, unique lines, visibility and stock checks,
  and Decimal subtotal.
- Coupons: active/expiry/minimum/category eligibility, fixed/percentage calculations,
  maximum caps, and nonnegative totals.
- Shipping: active methods, flat rates, local pickup, and pre-discount merchandise
  threshold for free shipping.
- Totals: subtotal minus discount plus shipping. Tax is explicitly `0.00`; the simulator
  provides no fictional tax rule.
- Checkout: validates customer, address ownership, cart, stock, shipping, and simulated
  payment method; calculates totals; creates a fictional order; changes stock; clears
  the persisted cart when present; and records safe activity. The unit of work returns
  to its prior snapshot on any failure.
- Account: fictional profile, order history/details/status summaries, and wishlist.
  These are demonstration views, not authentication.

No card, CVV, banking, credential, carrier, or payment-gateway data exists.

## Security services

Component risk uses only fixture update/support/lifecycle indicators. It does not query
a CVE or vulnerability service.

The educational score uses Phase 1 weights (critical 8, high 5, medium 3, low 1), finding
status factors, and control factors. Controls linked to findings are excluded to prevent
duplicate risk. Applicable unlinked controls remain in the maximum possible points even
when they pass. Scores are rounded whole numbers and mapped to four bands. For the
fixture, the before snapshot is **35 / High risk** and the after snapshot is
**83 / Guarded**. This is not certification.

Finding services filter, group, prioritize, identify quick wins, summarize effort and
business impact, and require explicit status changes. Snapshot comparison reports
score/band changes, opened/remediated findings, improved/regressed controls, component
versions, plugin risk, and remaining critical/high findings.

The JSON report is generated in memory with a deterministic structure. It contains
application/store identity, disclaimer, audit time, sanitized site summary, score,
findings, controls, plugins/themes, remediation plan, comparison, and privacy statement.
It excludes addresses, absolute paths, browser data, credentials, and external IDs.

## Hosted persistence limitation

A future Streamlit Community Cloud filesystem may reset at any time. Phase 4 must keep
session state primary and present persistence as optional demo behavior, never durable
customer storage.

## Phase 4 integration guidance

Phase 4 may build the storefront UI against a new per-session `ApplicationStateService`
and its services. It must require an explicit sample-load action, must not construct a
global unit of work, and must translate application exceptions into accessible messages.
It must not bypass service validation or call storage implicitly on rerun.

