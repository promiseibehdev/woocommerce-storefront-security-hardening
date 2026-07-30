# Architecture

## System boundary

WooCommerce Storefront & Security Hardening is an offline-first Streamlit engineering
simulator. It does not embed WordPress, WooCommerce, PHP, MySQL, a payment gateway, or a
live security scanner. All state is deterministic and fictional.

## Dependency direction

```text
app.py
  -> ui
      -> services
          -> repositories / state
              -> domain / serialization
          -> storage (only through explicit state actions)
sample_data -> domain / state / integrity
```

Domain and service modules do not import Streamlit. The presentation layer does not
reimplement commerce or scoring calculations.

## Domain and validation

Frozen, slotted dataclasses represent 14 commerce and 13 security concepts. `StrEnum`
types close status vocabularies. Each model validates local invariants during
construction; aggregate integrity validates uniqueness and relationships.

Money uses `Decimal` and cent quantization. Dates are timezone-aware. Fixture emails use
`example.test`, site labels use `.test`, and image references must be safe relative local
paths.

## Serialization

`to_primitive` converts declared dataclasses, enums, Decimal values, UTC timestamps,
dates, tuples, and string-key mappings into JSON-compatible primitives. `from_primitive`
uses resolved type hints and rejects unknown fields, wrong primitive types, unsupported
annotations, naive timestamps, invalid enum values, and invalid reconstructed models.

There is no pickle, arbitrary object construction, `eval`, or `exec`.

## Repositories and unit of work

`InMemoryRepository` owns a private mapping and provides deterministic list, get, find,
search, add, update, delete, replace, exists, and count operations. It rejects duplicate
keys and raises application-specific not-found/conflict errors.

Each `UnitOfWork` owns distinct repository instances. It can produce an immutable
`ApplicationState` snapshot or replace all state at a clear transaction boundary. There
is no module-level mutable repository or process-wide user data.

## Application state and session isolation

`ApplicationStateService` starts with `ApplicationState.empty()`. Streamlit stores one
service under a session-state key. No mutable service is decorated with `st.cache_data`
or `st.cache_resource`; separate visitors receive separate carts, wishlists, orders,
customer selections, remediation state, and fixture state.

Sample data is built only after the explicit **Load Fictional Sample Data** action.
Ordinary construction/import/startup creates no file or backup directory.

## Commerce services

- `CatalogueService`: visibility, text search, filters, stable sorts, related products,
  availability, and summary counts.
- `CartService`: cart mutations, visibility/stock limits, subtotal and transparent totals.
- `CouponService`: active/expiry/minimum/category/type/cap rules.
- `ShippingService`: active methods, flat rate, pickup, and free threshold.
- `CheckoutService`: validates the full command, computes through existing services,
  creates a fictional immutable order, updates stock, clears the stored cart, and records
  activity. It snapshots before mutation and restores on every failure.
- `AccountService`: fictional profile, order history/details/status, and wishlist.

Checkout has no sensitive payment fields and uses simulation-specific statuses.

## Security services

- `RiskService`: deterministic component/plugin/theme fixture indicators.
- `SecurityScoringService`: severity weights, status/control factors, duplicate-risk
  prevention, whole-number score, and bands.
- `FindingService`: query/group/prioritize/quick-win/remediation operations.
- `ComparisonService`: immutable snapshot changes.
- `SecurityDashboardService`: presentation-focused joins and current-audit summaries.
- `SecurityReportService`: allowlisted in-memory JSON report.

No service queries a CVE source or WordPress endpoint.

## Storage, atomic writes, backup, and recovery

`JsonStateStore` is opt-in and receives an explicit path. Its versioned envelope contains
schema version, application identity, application version, saved timestamp, and payload.

Save:

1. Validate the complete aggregate.
2. Encode deterministic UTF-8 JSON.
3. Create the destination directory only on explicit save.
4. Validate/back up an existing destination.
5. Write a unique same-directory temporary file.
6. Flush and `fsync`.
7. Atomically replace with `os.replace`.
8. Remove a remaining temporary file on failure.

Load validates the envelope, schema, typed payload, and aggregate before returning state.
Malformed/corrupt input is preserved. Restore accepts only a managed validated backup and
preserves a corrupt current file under a timestamped name.

Schema remains `1`; the explicit migration registry has no invented version-2 structure.

## Streamlit presentation

`app.py` adds the local `src` directory and calls the shell. The shell supplies the
Storefront/Security switcher, grouped navigation, explicit sample load, customer demo
context, and safe application-error boundary.

Storefront and Security renderers call services and format returned values. Shared
components provide headings, cards, status labels, empty states, notices, and minimal
responsive CSS.

## Offline-first and privacy

Runtime code has no HTTP client dependency, remote asset, external font, tracker,
analytics SDK, or authentication integration. The package has one runtime dependency:
Streamlit.

Reports omit addresses, absolute paths, browser state, secrets, and credentials. All
fixture identities are fictional and deterministic.

## Limitations

- Single-process local JSON semantics; no concurrent database transaction guarantees.
- Streamlit Community Cloud storage is ephemeral.
- No production tax, gateway, authentication, fulfillment, or inventory concurrency.
- No live security assessment or formal certification.
- Streamlit owns browser rendering/focus details; formal WCAG conformance is not claimed.

