# WooCommerce Storefront & Security Hardening

## Phase 1 — Architecture and Implementation Specification

**Status:** Phase 1 planning only  
**Application type:** Offline-first Streamlit portfolio engineering simulator  
**Target runtime:** Python 3.12 and Streamlit  
**Fictional store:** Northstar Desk & Living  
**Document version:** 1.0.0  
**Prepared:** 2026-07-30

> This project is a portfolio engineering simulator inspired by common WooCommerce environments. It is not connected to a real WordPress or WooCommerce installation, does not process payments, does not collect or store real customer information, and uses fictional products, people, orders, accounts, and security findings.

---

## 1. Executive summary

WooCommerce Storefront & Security Hardening will combine two coordinated demonstration workspaces:

1. A realistic but fictional ecommerce storefront for Northstar Desk & Living, a modern electronics, home-office, and lifestyle retailer.
2. A security engineering workspace that explains how WordPress and WooCommerce risks can be reviewed, scored, prioritized, remediated, and verified.

The application will simulate commerce and security workflows with deterministic local data. It will not run WordPress, WooCommerce, PHP, a payment gateway, or a live scanner. Its value is in the domain modeling, validation, repository and service design, transparent scoring, accessible UI, privacy controls, and meaningful automated tests.

The architecture uses a small layered Python package: immutable or validation-oriented domain models; explicit serializers; JSON repositories behind storage ports; pure business services; deterministic sample-data factories; and thin Streamlit presentation modules. Imports and ordinary startup remain side-effect free. Sample data and writable storage are created only following an explicit user action.

## 2. Project identity

- **Official title:** WooCommerce Storefront & Security Hardening
- **Fictional store:** Northstar Desk & Living
- **Positioning:** Portfolio engineering simulator and security demonstration
- **Audience:** Recruiters, engineering reviewers, ecommerce stakeholders, and security-minded developers
- **Tone:** Professional, practical, educational, and candid about limitations
- **Primary disclaimer:** No live WordPress/WooCommerce system is present or assessed.
- **Commerce disclaimer:** No real transaction occurs and no payment credential is requested.
- **Data disclaimer:** Every product, person, account, address, order, event, and finding is fictional.

These statements will appear in the Store Information view, the Security Overview methodology panel, checkout, exported reports, and the eventual README.

## 3. Scope

### 3.1 Storefront scope

- Store landing dashboard with featured, sale, and low-stock products
- Catalogue search, filters, sorting, categories, product details, ratings, and stock
- Session cart with quantity management, coupons, shipping estimates, and totals
- Checkout simulation with fictional customer/address data and non-sensitive payment-method selection
- Simulated order confirmation and order history
- Wishlist/saved products
- Store information, policies, and explicit simulation limitations
- Responsive layouts suitable for desktop and narrow screens

### 3.2 Security scope

- Version posture for simulated WordPress core, WooCommerce, PHP, plugins, and themes
- Plugin lifecycle and vulnerability indicators
- User/account, login, configuration, file, transport, backup, logging, API, checkout, payment, privacy, reliability, and accessibility controls
- Findings with evidence, impact, remediation, ownership/priority, effort, and verification
- Transparent educational risk score
- Before/after audit comparison
- JSON report export containing fictional data only
- Explicit sample reset/reload workflow

### 3.3 Engineering scope

- Typed domain models using Python standard-library dataclasses and enums
- Centralized validation and Decimal-based money calculations
- Repository interfaces, atomic JSON persistence, schema versioning, and corruption recovery
- Pure service functions where practical
- Pytest, Ruff, GitHub Actions, architecture/security documentation, and release checklists

## 4. Explicit non-goals

- Running, embedding, emulating, or claiming to run WordPress, WooCommerce, PHP, MySQL, or a web server
- Connecting to WordPress REST/XML-RPC endpoints or WooCommerce APIs
- Real authentication, authorization, or role-based access control
- Real malware scanning, vulnerability scanning, penetration testing, or certification
- Real payments, card entry, bank details, payment tokens, refunds, tax advice, or fulfillment
- Real customers, companies, accounts, addresses, credentials, orders, or analytics
- External APIs, remote images, tracking, cloud databases, paid services, or authentication providers
- Production-grade inventory concurrency or multi-user persistence
- Representing the educational score as an industry standard, compliance result, guarantee, or formal audit
- Docker or a JavaScript framework without later explicit justification

## 5. User experiences

### 5.1 Storefront workspace

A visitor explores Northstar Desk & Living as a customer would: browse products, inspect details, save items, build a cart, choose delivery, complete a clearly simulated checkout, and inspect fictional order history.

### 5.2 Security workspace

A reviewer explores the same fictional store as a security engineer or store manager demonstration view. The workspace explains posture, findings, controls, component risks, remediation priorities, and verified before/after improvements.

### 5.3 Demonstration views, not roles

“Customer view,” “Store manager view,” and “Security engineer view” are presentation contexts only. They do not authenticate a person, enforce permissions, or represent role-based access control. The workspace switcher must label them as **Demo view**. Any future UI control that switches views changes presentation, not authorization.

## 6. Navigation structure

Use one persistent sidebar with a workspace switcher and compact destinations. Detailed subsections use tabs, filters, expanders, and contextual links rather than more sidebar pages.

### Storefront

1. **Store Home** — merchandising highlights, store summary, featured/sale products
2. **Shop** — catalogue, search, category/price/stock filters, sorting; product details open contextually
3. **Cart & Checkout** — cart, coupon, shipping, checkout, and confirmation as a step flow
4. **My Store** — account summary, order history, and wishlist as tabs
5. **Store Information** — policies, simulator disclosures, accessibility and privacy notes

### Security

1. **Security Overview** — score, posture cards, severity summary, failed/passed controls, methodology
2. **Components** — Core & Runtime, Plugins, and Themes tabs
3. **Access & Configuration** — Users & Access, Login Protection, Files & Configuration, and API Exposure tabs
4. **Commerce & Data Protection** — Checkout & Payments, Privacy & Retention, Backups & Activity tabs
5. **Remediation & Comparison** — plan, quick wins, before/after, verification, and report export

Performance/reliability and accessibility reviews are surfaced as security/control categories and overview panels rather than separate sidebar destinations.

## 7. Feature catalogue

| Capability | Planned behavior | Workspace |
|---|---|---|
| Catalogue | Search, filter, sort, paginate/limit display, open product details | Storefront |
| Merchandising | Featured, sale, availability, ratings, categories | Storefront |
| Cart | Add, update, remove, subtotal and validation | Storefront |
| Promotions | Eligible fixed/percentage coupons with deterministic rules | Storefront |
| Shipping | Method eligibility and Decimal-based fees | Storefront |
| Checkout | Validate fictional data; select a simulated payment method | Storefront |
| Orders | Create simulated order, reduce simulated stock, show confirmation/history | Storefront |
| Wishlist | Add/remove and move eligible items to cart | Storefront |
| Posture | Score, rating, control state, risk summary | Security |
| Components | Version/update/plugin/theme lifecycle indicators | Security |
| Findings | Severity, status, evidence, impact, remediation, verification | Security |
| Remediation | Priority queue, effort, quick wins, status changes | Security |
| Comparison | Before/after snapshots and traceable improvement explanations | Security |
| Reporting | Download fictional JSON report with methodology metadata | Security |
| Reset | Explicit preview/confirmation and deterministic sample reset | Shared |

## 8. Domain models

Models use `@dataclass` with explicit construction validation. IDs are stable prefixed strings generated deterministically for samples and with UUID-derived suffixes for simulated new orders. Dates use ISO-8601 strings at the JSON boundary and timezone-aware UTC `datetime` values in the domain. Money uses `Decimal`, serialized as fixed-point strings.

### 8.1 Storefront models

#### ProductCategory

- **Purpose:** Product grouping and navigation.
- **Required:** `id`, `name`, `slug`, `description`
- **Optional:** `parent_id`, `image_ref`, `display_order`
- **Enums:** none
- **Validation:** unique ID/slug; lowercase URL-safe slug; parent cannot equal self; nonnegative display order
- **Relationships:** one category has many products; optional self-parent
- **Serialization:** plain object; image is a relative local asset reference

#### Product

- **Purpose:** Sellable catalogue item.
- **Required:** `id`, `sku`, `name`, `slug`, `description`, `short_description`, `category_id`, `regular_price`, `stock_quantity`, `stock_status`, `featured`, `rating`, `review_count`, `image_ref`, `tags`, `visibility`, `created_at`, `updated_at`
- **Optional:** `sale_price`, `low_stock_threshold`, `weight_kg`, `specifications`
- **Enums:** `StockStatus`, `ProductVisibility`
- **Validation:** unique ID/SKU/slug; nonblank text; nonnegative prices/stock; sale price positive and below regular price; rating 0–5; review count nonnegative; category exists; stock status agrees with quantity; timestamps ordered; local relative image path only
- **Relationships:** belongs to one category; has zero or more reviews; referenced by cart/order/wishlist items
- **Serialization:** Decimal as string, enums as values, timestamps as UTC ISO-8601

#### ProductReview

- **Purpose:** Fictional product feedback.
- **Required:** `id`, `product_id`, `display_name`, `rating`, `title`, `body`, `created_at`, `verified_purchase`
- **Optional:** none
- **Enums:** none
- **Validation:** rating integer 1–5; fictional non-email display name; bounded title/body; product exists
- **Relationships:** belongs to one product
- **Serialization:** standard typed object

#### CartItem

- **Purpose:** Quantity and price reference for a cart line.
- **Required:** `product_id`, `quantity`
- **Optional:** none
- **Enums:** none
- **Validation:** quantity integer 1–99; product visible and purchasable; quantity does not exceed stock
- **Relationships:** belongs to a cart; references a product
- **Serialization:** persist identifiers and quantity, never copied totals

#### Cart

- **Purpose:** Current basket state.
- **Required:** `id`, `items`
- **Optional:** `coupon_code`, `shipping_method_id`, `updated_at`
- **Enums:** none
- **Validation:** unique product lines; referenced coupon/shipping method valid when set
- **Relationships:** aggregates cart items; references coupon and shipping method
- **Serialization:** derived totals excluded and recalculated

#### Coupon

- **Purpose:** Deterministic promotion rule.
- **Required:** `code`, `discount_type`, `amount`, `active`
- **Optional:** `minimum_subtotal`, `maximum_discount`, `eligible_category_ids`, `expires_at`, `usage_limit`
- **Enums:** `DiscountType`
- **Validation:** uppercase normalized code; positive amount; percentage at most 100; valid categories; dates valid
- **Relationships:** optionally targets categories; may be applied to carts/orders
- **Serialization:** Decimal values as strings

#### ShippingMethod

- **Purpose:** Simulated delivery option and fee.
- **Required:** `id`, `name`, `description`, `base_fee`, `active`
- **Optional:** `free_above`, `estimated_days_min`, `estimated_days_max`
- **Enums:** none
- **Validation:** nonnegative fee; valid day range; free threshold positive
- **Relationships:** selected by cart/order
- **Serialization:** Decimal values as strings

#### PaymentMethod

- **Purpose:** Non-sensitive simulated payment choice.
- **Required:** `id`, `name`, `description`, `active`, `simulation_notice`
- **Optional:** `display_order`
- **Enums:** `PaymentMethodKind`
- **Validation:** no fields for card/bank credentials; notice mandatory; known kind only
- **Relationships:** selected by order
- **Serialization:** configuration only

#### Customer

- **Purpose:** Fictional account profile.
- **Required:** `id`, `display_name`, `email`, `created_at`
- **Optional:** `default_billing_address_id`, `default_shipping_address_id`
- **Enums:** none
- **Validation:** email-shaped reserved fictional address under `example.test`; no password/auth fields
- **Relationships:** owns addresses, orders, and wishlist items
- **Serialization:** fictional profile object

#### Address

- **Purpose:** Fictional billing/shipping details for validation demonstration.
- **Required:** `id`, `customer_id`, `kind`, `recipient_name`, `line_1`, `city`, `region`, `postal_code`, `country_code`
- **Optional:** `line_2`
- **Enums:** `AddressKind`
- **Validation:** bounded text, fictional fixture marker, supported country code; no phone required
- **Relationships:** belongs to customer; snapshots into order
- **Serialization:** object; order receives a value snapshot, not a mutable reference

#### OrderItem

- **Purpose:** Immutable purchased-item snapshot.
- **Required:** `product_id`, `sku`, `name`, `unit_price`, `quantity`, `line_total`
- **Optional:** none
- **Enums:** none
- **Validation:** positive quantity; line total equals rounded unit price × quantity
- **Relationships:** belongs to order; references original product ID while retaining display snapshot
- **Serialization:** Decimal values as strings

#### Order

- **Purpose:** Simulated transaction record.
- **Required:** `id`, `order_number`, `customer_id`, `items`, `status`, `payment_method_id`, `payment_status`, `shipping_method_id`, address snapshots, `subtotal`, `discount_total`, `shipping_total`, `grand_total`, `created_at`, `simulation_notice`
- **Optional:** `coupon_code`, `customer_note`, `updated_at`
- **Enums:** `OrderStatus`, `PaymentSimulationStatus`
- **Validation:** at least one line; totals reconcile; required address fields; status transition allowed; mandatory simulation notice; no payment credentials
- **Relationships:** belongs to customer; aggregates item and address snapshots
- **Serialization:** complete immutable financial snapshot

#### WishlistItem

- **Purpose:** Saved product reference.
- **Required:** `customer_id`, `product_id`, `created_at`
- **Optional:** none
- **Enums:** none
- **Validation:** unique customer/product pair; referenced records exist
- **Relationships:** joins customer and product
- **Serialization:** compact reference

#### StoreSettings

- **Purpose:** Simulator-wide commerce configuration.
- **Required:** `store_name`, `currency_code`, `currency_symbol`, `low_stock_default`, `catalogue_page_size`, `schema_version`
- **Optional:** `announcement`, `tax_display_notice`
- **Enums:** none
- **Validation:** supported currency, positive thresholds/page size; fictional store identity fixed in samples
- **Relationships:** used by services/UI
- **Serialization:** singleton object

### 8.2 Security models

#### SiteProfile

- **Purpose:** Fictional installation context.
- **Required:** `id`, `site_name`, `environment`, `base_url_label`, `wordpress_version`, `woocommerce_version`, `php_version`, `https_enabled`, `captured_at`
- **Optional:** `notes`
- **Enums:** `EnvironmentKind`
- **Validation:** URL must use reserved `.test`; semantic-like versions; explicitly marked simulated
- **Relationships:** root of audit snapshots

#### CoreComponent

- **Purpose:** Version/update posture for WordPress, WooCommerce, or PHP.
- **Required:** `id`, `name`, `component_type`, `installed_version`, `recommended_version`, `update_status`, `support_status`
- **Optional:** `end_of_support_date`
- **Enums:** `CoreComponentType`, `UpdateStatus`, `SupportStatus`
- **Validation:** known type; version strings bounded; status consistent with versions

#### Plugin

- **Purpose:** Plugin inventory and lifecycle risk.
- **Required:** `id`, `name`, `slug`, `version`, `status`, `update_status`, `last_updated_on`, `publisher`, `vulnerability_indicator`, `business_purpose`
- **Optional:** `recommended_version`, `abandoned`, `known_issue_summary`, `replacement_candidate`
- **Enums:** `PluginStatus`, `UpdateStatus`, `VulnerabilityIndicator`
- **Validation:** inactive and active are explicit; abandoned based on fixture rule; indicator is educational, not live intelligence
- **Relationships:** may be affected component of findings/controls

#### Theme

- **Purpose:** Active/installed theme and child-theme posture.
- **Required:** `id`, `name`, `version`, `status`, `update_status`, `is_child_theme`
- **Optional:** `parent_theme_id`, `recommended_version`, `last_updated_on`
- **Enums:** `ThemeStatus`, `UpdateStatus`
- **Validation:** a child theme requires parent; one active theme; parent exists; versions valid

#### UserAccount

- **Purpose:** Fictional account/access posture.
- **Required:** `id`, `display_name`, `email`, `account_type`, `is_administrator`, `two_factor_enabled`, `password_policy_status`, `last_login_at`, `active`
- **Optional:** `notes`
- **Enums:** `AccountType`, `ControlStatus`
- **Validation:** reserved fictional email; no password/hash/token; admin count and stale-account rules are evaluated by services

#### SecurityCategory

- **Purpose:** Stable taxonomy and presentation metadata.
- **Required:** `id`, `name`, `description`, `display_order`
- **Optional:** none
- **Enums:** none
- **Validation:** unique ID/name/order

#### SecurityControl

- **Purpose:** Expected safeguard and current state.
- **Required:** `id`, `category_id`, `title`, `description`, `status`, `importance`, `evidence_summary`, `verification_guidance`
- **Optional:** `related_component_id`, `finding_id`
- **Enums:** `ControlStatus`, `Severity`
- **Validation:** failed controls should reference a finding unless documented as accepted/not applicable; evidence mandatory

#### SecurityFinding

- **Purpose:** Actionable risk record.
- **Required:** `id`, `title`, `category_id`, `severity`, `status`, `affected_component`, `description`, `evidence`, `business_impact`, `recommended_remediation`, `priority`, `estimated_effort`, `before_state`, `after_state`, `verification_status`
- **Optional:** `control_ids`, `owner_label`, `target_phase`, `accepted_risk_reason`
- **Enums:** `Severity`, `FindingStatus`, `RemediationPriority`, `EstimatedEffort`, `VerificationStatus`
- **Validation:** evidence/impact/remediation nonblank; remediated requires after state and verified/pending verification; accepted risk requires reason; IDs unique

#### RemediationAction

- **Purpose:** Track a concrete response to a finding.
- **Required:** `id`, `finding_id`, `title`, `priority`, `effort`, `status`, `verification_steps`
- **Optional:** `owner_label`, `due_label`, `completed_at`, `notes`
- **Enums:** `RemediationPriority`, `EstimatedEffort`, `RemediationStatus`
- **Validation:** completed requires completion date; verified finding requires completed action and verification evidence

#### ScanSummary

- **Purpose:** Derived, explicitly simulated posture summary.
- **Required:** `snapshot_id`, `open_counts_by_severity`, `control_counts_by_status`, `risk_points`, `maximum_applicable_points`, `score_band`, `generated_at`, `methodology_version`, `simulation_notice`
- **Optional:** none
- **Enums:** `RiskLevel`
- **Validation:** counts/totals reconcile; never treated as authoritative stored input

#### AuditSnapshot

- **Purpose:** Immutable before/after audit state.
- **Required:** `id`, `label`, `captured_at`, `site_profile`, `component_refs`, `control_states`, `finding_states`, `methodology_version`
- **Optional:** `notes`, `previous_snapshot_id`
- **Enums:** `SnapshotKind`
- **Validation:** immutable after creation; referenced records exist; before/after methodology versions comparable

#### BackupRecord

- **Purpose:** Fictional backup posture/history.
- **Required:** `id`, `started_at`, `completed_at`, `backup_type`, `status`, `restore_tested`
- **Optional:** `retention_days`, `notes`
- **Enums:** `BackupType`, `BackupStatus`
- **Validation:** timestamps ordered; successful record requires completion; retention nonnegative

#### ActivityEvent

- **Purpose:** Fictional security/administrative timeline.
- **Required:** `id`, `occurred_at`, `actor_label`, `event_type`, `summary`, `outcome`
- **Optional:** `component_ref`, `metadata`
- **Enums:** `ActivityEventType`, `ActivityOutcome`
- **Validation:** no secret values; metadata allowlist; chronological sorting

## 9. Validation rules

Validation is applied at four boundaries:

1. **Model construction:** field types, required values, ranges, enum membership, local invariants.
2. **Dataset validation:** uniqueness, referential integrity, category/account/product links, single active theme, derived rating consistency.
3. **Service commands:** stock, coupon, shipping, checkout, state transitions, remediation/verification prerequisites.
4. **Persistence load:** schema version, JSON shape, checksums where supported, and full domain reconstruction before replacing current state.

Shared rules:

- Strip surrounding whitespace; reject blank required strings.
- Cap user-entered demo text lengths and render as text, never unsafe HTML.
- Use `Decimal("0.01")` half-up currency quantization.
- Use UTC-aware timestamps; display dates in a documented demo timezone.
- Normalize SKU, coupon code, and safe identifiers consistently.
- Never trust stored derived totals or risk summaries; recalculate them.
- Reject absolute paths, `..`, and remote schemes in image references.
- Require reserved domains such as `example.test` for fictional email/site fixtures.
- Emit field-specific, accessible error messages without exposing stack traces.

## 10. Enums

| Enum | Planned values |
|---|---|
| StockStatus | `in_stock`, `low_stock`, `out_of_stock` |
| ProductVisibility | `visible`, `hidden` |
| DiscountType | `fixed_cart`, `percentage` |
| PaymentMethodKind | `demo_card`, `bank_transfer_simulation`, `cash_on_delivery_simulation`, `digital_wallet_simulation` |
| OrderStatus | `pending`, `processing`, `on_hold`, `completed`, `cancelled`, `refunded_simulation` |
| PaymentSimulationStatus | `not_started`, `authorized_simulation`, `pending_simulation`, `failed_simulation`, `not_required` |
| Severity | `critical`, `high`, `medium`, `low`, `informational` |
| FindingStatus | `open`, `in_progress`, `remediated`, `accepted`, `not_applicable` |
| ControlStatus | `pass`, `fail`, `partial`, `not_applicable` |
| PluginStatus | `active`, `inactive`, `must_use` |
| UpdateStatus | `current`, `update_available`, `unsupported`, `unknown` |
| RiskLevel | `low`, `guarded`, `elevated`, `high` |
| RemediationPriority | `immediate`, `next`, `planned`, `monitor` |
| EstimatedEffort | `small`, `medium`, `large` |
| VerificationStatus | `not_started`, `pending`, `verified`, `failed` |
| RemediationStatus | `todo`, `in_progress`, `completed`, `blocked` |

Additional narrow enums (`AddressKind`, theme/component/support/backup/activity/snapshot kinds and outcomes) prevent string drift without adding domain objects that lack behavior.

## 11. Relationships

```text
ProductCategory 1 ── * Product 1 ── * ProductReview
                            │
Customer 1 ── * CartItem * ┘
    │           Cart ── Coupon / ShippingMethod
    ├── * Address
    ├── * Order 1 ── * OrderItem ── Product (reference + snapshot)
    └── * WishlistItem * ── Product

SiteProfile 1 ── * AuditSnapshot
AuditSnapshot ── component/control/finding state snapshots
SecurityCategory 1 ── * SecurityControl
SecurityCategory 1 ── * SecurityFinding
SecurityFinding 1 ── * RemediationAction
SecurityControl * ── 0..1 SecurityFinding
Plugin / Theme / CoreComponent / UserAccount ── affected-component references
```

Relationships use stable IDs in JSON. Services resolve references through repositories and validators reject dangling IDs.

## 12. Security scoring methodology

### 12.1 Purpose and disclaimer

The score is a deterministic educational portfolio measure, not a certification, CVSS implementation, compliance result, or prediction of compromise. The UI and exported report label it **Simulated Security Posture Score** and show the methodology/version.

### 12.2 Risk points

Only applicable controls and non-accepted open findings contribute risk.

Finding base weights:

- Critical: 8
- High: 5
- Medium: 3
- Low: 1
- Informational: 0

Finding status factor:

- Open: 1.0
- In progress: 0.75
- Remediated, verified: 0
- Remediated, pending verification: 0.25
- Accepted: 0.5, with visible accepted-risk label and rationale
- Not applicable: excluded

Control points use the control’s importance weight (same 8/5/3/1 scale):

- Fail: 1.0 × weight
- Partial: 0.5 × weight
- Pass: 0
- Not applicable: excluded

To prevent double counting, a failed/partial control linked to a finding is represented by the finding points only. Unlinked control failures contribute control points. This rule is tested.

### 12.3 Score and bands

`maximum_applicable_points` is the sum of base weights for all applicable findings plus unlinked applicable controls. `risk_points` applies the status factors above.

The score is intentionally shown as a rounded whole-number index:

`posture_score = round(100 × (1 - risk_points / maximum_applicable_points))`

If no applicable checks exist, show “Not scored,” not 100.

Rating bands:

- 85–100: Low risk
- 70–84: Guarded
- 50–69: Elevated
- 0–49: High risk

The primary presentation includes the band and open critical/high counts; the numeric index is secondary to avoid fake precision. The interface explains which findings/control changes altered the result.

### 12.4 Remediation effect

Changing a finding to in-progress lowers but does not erase its risk. “Remediated” without verification retains 25%. Only verified remediation removes its points. Before/after comparison uses immutable snapshots and the same methodology version; otherwise it warns that direct score comparison is invalid.

## 13. Storefront workflows

### Search, filtering, and sorting

- Normalize query case/whitespace; match product name, SKU, short description, tags, and category.
- Combine category, inclusive price range, stock state, featured/sale flags using AND semantics; multi-select values within one filter use OR.
- Price filtering uses effective sale price.
- Sort by relevance (when searching), featured/default order, newest, price low/high, rating, or name.
- Preserve filters in session state; “Clear filters” restores documented defaults.
- Show result count and accessible empty-state recovery action.

### Cart

- Adding validates visibility and current sample stock; repeated adds increment within stock/99 limit.
- Quantity update recalculates all derived totals; invalid quantities show a field error.
- Remove requires one explicit click and is reversible by adding again.
- Cart never stores copied product prices; current catalogue prices drive pre-order totals.

### Coupons and shipping

- Coupon codes normalize to uppercase; service checks active/expiry/minimum/category rules.
- One coupon per cart for initial scope; rejection explains why.
- Percentage discount applies to eligible merchandise subtotal and respects maximum discount.
- Shipping method eligibility is recalculated after discount according to a documented rule: free-shipping threshold uses pre-discount merchandise subtotal.
- Totals order: merchandise subtotal → discount → shipping → grand total. Taxes are explicitly “not calculated in this simulator.”

### Checkout and order placement

1. Review cart and stock.
2. Enter/select fictional demonstration customer and address information.
3. Select a shipping method.
4. Select a simulated payment method; never request card/account credentials.
5. Show mandatory notice: “No real payment is processed. Do not enter payment credentials. This transaction is simulated.”
6. Validate fields, cart, stock, coupon, totals, and method availability.
7. Create an immutable order snapshot, decrement simulated inventory, and clear cart as one service transaction.
8. Show confirmation with simulated order number, totals, and notice.

Order creation uses an idempotency token in session state to avoid duplicate orders on Streamlit reruns. Failed validation creates no order and changes no inventory.

### Account, history, and wishlist

- Demo customer selection is not login/authentication.
- History filters fictional orders by selected demo customer and shows status/totals/details.
- Wishlist add/remove is unique per customer/product.
- “Move to cart” checks visibility/stock; successful add may optionally remove from wishlist.

## 14. Security-audit workflows

- **Load:** User explicitly selects “Load fictional demo dataset”; validator completes before state becomes active.
- **Overview:** Scoring service derives score, band, counts, top risks, and control coverage.
- **Triage:** Filter findings by severity/category/status/priority/effort; sort deterministically by severity, priority, then ID.
- **Controls:** Separate passed, partial, failed, and not-applicable lists; always include text labels.
- **Components:** Evaluate versions, update/lifecycle state, abandonment, active/inactive inventory, theme/child theme, and plugin-count risk rules.
- **Remediate:** Change action state; enforce prerequisites; show expected score impact as an estimate.
- **Verify:** Record verification result/evidence before full risk removal.
- **Compare:** Select immutable before/after snapshots; show resolved/new/unchanged/regressed findings, control transitions, and score-band change.
- **Quick wins:** Open high-value actions with small estimated effort, ordered by severity/weight and deterministic tie-breaker.
- **Business impact:** Every actionable finding includes a plain-language commerce/reputation/availability/privacy impact.
- **Export:** Generate report JSON in memory for Streamlit download; include disclaimers, schema/methodology versions, timestamp, fictional marker, summaries, findings, controls, and remediation plan. Exclude session internals and unnecessary fictional addresses.
- **Reset:** Preview what will change, require explicit confirmation, atomically replace writable state with deterministic samples, and retain/recover previous file as documented backup where available.

## 15. Storage strategy

### 15.1 Principles

- Importing modules performs no I/O, directory creation, environment mutation, or sample generation.
- Basic Streamlit startup displays a welcome/consent screen and creates no working data.
- The explicit “Load fictional demo dataset” action constructs data in memory. Persistence is separately opt-in with “Enable local demo persistence.”
- Streamlit Community Cloud is treated as ephemeral; hosted data may reset at any time.

### 15.2 Persistence boundaries

| Data | Default | Optional persisted form |
|---|---|---|
| Catalogue/categories/reviews | Read-only deterministic fixture factory | None |
| Cart | Session-only | `commerce_state.json` |
| Simulated new orders | Session-only | `commerce_state.json` |
| Wishlist | Session-only | `commerce_state.json` |
| Demo customer selection | Session-only | Never |
| Security remediation changes | Session-only | `security_state.json` |
| Store settings overrides | Session-only | `settings.json` |
| Audit snapshots | Loaded deterministic fixtures/session | `security_state.json` |
| UI filters/navigation | Session-only | Never |
| Export report | In-memory download | Never written automatically |

### 15.3 File layout and atomic writes

An explicitly selected writable directory contains:

```text
.demo_data/
├── manifest.json
├── commerce_state.json
├── security_state.json
├── settings.json
└── backups/
```

Each document contains `schema_version`, `dataset_id`, `updated_at`, and `payload`. Write JSON to a uniquely named temporary file in the same directory, flush and `fsync`, validate by rereading, then replace the target atomically with `os.replace`. A bounded previous-good backup is created before replacement. A repository-level lock is not promised; the app is a single-session simulator.

### 15.4 Corruption and migration

- Parse into untrusted dictionaries, validate schema/version and reconstruct full models.
- On failure, leave the corrupt file untouched, do not partially load it, show a safe diagnostic, and offer download/rename plus restoration from a validated backup.
- Never silently reset or overwrite corrupt data.
- Migrations are explicit, version-to-version, tested, and create a backup first.
- Hosted persistence limitations are prominent in README/deployment documentation.

## 16. Layered architecture

1. **Domain:** Dataclasses, enums, domain errors, invariant validation; no Streamlit or filesystem imports.
2. **Application/services:** Cart, checkout, catalogue, scoring, remediation, comparison, report, and reset use cases; depends on domain and repository protocols.
3. **Repository:** Interfaces and JSON/in-memory implementations; maps serialized documents to domain entities.
4. **Storage:** Atomic file operations, schema envelopes, migrations, corruption handling.
5. **Sample data:** Pure deterministic factories and integrity validation; no writes.
6. **Presentation:** Streamlit pages/components/session adapters; invokes services and translates errors into accessible messages.
7. **Bootstrap:** Dependency assembly after explicit user action; `app.py` remains a thin entry point.

Dependency direction is inward. Domain and application layers never import Streamlit. In-memory repositories support fast unit tests and default session-only operation.

## 17. Proposed folder structure

```text
woocommerce-storefront-security-hardening/
├── app.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── products/
│   ├── icons/
│   └── screenshots/
├── src/
│   └── woo_security_simulator/
│       ├── __init__.py
│       ├── bootstrap.py
│       ├── domain/
│       │   ├── commerce.py
│       │   ├── security.py
│       │   ├── enums.py
│       │   ├── validation.py
│       │   └── errors.py
│       ├── application/
│       │   ├── catalogue_service.py
│       │   ├── cart_service.py
│       │   ├── checkout_service.py
│       │   ├── security_score_service.py
│       │   ├── remediation_service.py
│       │   ├── comparison_service.py
│       │   └── report_service.py
│       ├── repositories/
│       │   ├── protocols.py
│       │   ├── memory.py
│       │   └── json_repository.py
│       ├── storage/
│       │   ├── atomic_json.py
│       │   ├── envelopes.py
│       │   └── migrations.py
│       ├── sample_data/
│       │   ├── factory.py
│       │   └── integrity.py
│       └── ui/
│           ├── shell.py
│           ├── state.py
│           ├── components/
│           ├── storefront/
│           └── security/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── smoke/
│   └── fixtures/
├── docs/
│   ├── PHASE_1_ARCHITECTURE.md
│   ├── TESTING.md
│   ├── SECURITY_METHODOLOGY.md
│   ├── DEPLOYMENT.md
│   ├── SCREENSHOTS.md
│   └── RELEASE_CHECKLIST.md
└── .github/
    └── workflows/
        └── quality.yml
```

Only `docs/PHASE_1_ARCHITECTURE.md` exists in Phase 1. The rest is the planned structure.

## 18. Sample-data plan

All fixtures use reserved domains and obviously fictional identities.

- **Products:** 20 across 6 categories: Desk Technology, Audio & Video, Lighting, Ergonomics, Organization, and Everyday Carry.
- **Merchandising mix:** 5 featured, 6 on sale, 12 normally in stock, 4 low stock, 1 out of stock, and remaining overlap as appropriate.
- **Reviews:** 8 across at least 6 products; product aggregate ratings/counts validated against review fixtures or clearly flagged as aggregate sample data.
- **Customers:** 4 fictional customers using `@example.test`.
- **Orders:** 8 spanning pending, processing, on-hold, completed, cancelled, and refund-simulation states.
- **Shipping:** Standard Delivery, Express Delivery, and Local Pickup (3).
- **Payments:** Demo Card (label only), Simulated Bank Transfer, Cash on Delivery Simulation, and Demo Digital Wallet (4); no credential fields.
- **Coupons:** `DESK10` percentage coupon and `WELCOME15` fixed-cart coupon with deterministic eligibility.
- **Plugins:** 11 fictionalized or generic-purpose inventory entries; at least 1 outdated, 2 inactive, 1 abandoned/high-risk indicator, and 1 excessive-plugin-footprint finding. Names avoid implying a live vulnerability feed.
- **Themes:** 2: active Northstar Child and installed Northstar Base parent; child-theme posture represented.
- **Accounts:** 6 across administrator, editor/store-manager demo label, and customer types; at least 2 fictional admins, one without 2FA, and one stale/inactive account.
- **Controls:** 22 across core/runtime, components, access, login, configuration/files, transport/headers, backup/logging, API exposure, checkout/payment, privacy/retention, reliability, and accessibility.
- **Findings:** 14 with a balanced severity distribution, including outdated/abandoned plugin, weak admin controls, XML-RPC exposure, file editing/debug posture, backup restore testing, security headers, enumeration/API, retention/privacy, and checkout hardening.
- **Snapshots:** One vulnerable “Before hardening” and one “After prioritized remediation,” with traceable control/finding transitions.
- **Operational records:** 5 backup records and 12 activity events.

Examples of products may include Northstar Arc Monitor Light, Meridian USB-C Dock, QuietKey Compact Keyboard, Vale Laptop Stand, Orbit Cable Tray, and Fieldnote Tech Pouch. All brand/store/product identities are invented and checked against a local denylist of real user information.

Sample generation accepts a fixed seed/version but avoids randomness where explicit fixtures are clearer. Integrity tests assert exact counts, uniqueness, relationships, stock mix, statuses, disclaimers, reserved-domain usage, and absence of secret-like fields.

## 19. UI design system

- **Visual identity:** Calm neutral surfaces, deep slate text, restrained blue primary actions, green/amber/red status accents, generous whitespace.
- **Typography:** Streamlit/system sans serif, clear hierarchy, minimum readable body size; no tiny metadata.
- **Shell:** Branded title, persistent simulator badge, workspace switcher, compact sidebar, current-view label.
- **Cards:** Product cards with local image, name, price/sale label, rating text, and stock badge; summary cards with label, value, context.
- **Statuses:** Icon + text + color (for example, “High severity”), never color alone.
- **Tables:** Mobile-conscious column selection, deterministic sorting, accessible labels; details open below rather than horizontal overload.
- **Forms:** Grouped fields, inline guidance, explicit required labels, validation summary, single clear primary action.
- **Charts:** Optional and supplementary only; every chart has an adjacent textual/table equivalent.
- **Motion:** No unnecessary animation.
- **Empty/error states:** Explain what happened and offer a safe next action.
- **Product images:** Small, locally stored WebP/PNG illustrations or consistent abstract placeholders created for this fictional catalogue; descriptive alt/caption text lives in product metadata. No runtime remote downloads.

Custom CSS, if required, will be minimal, tested at narrow widths, and avoid brittle selectors against Streamlit internals.

## 20. Accessibility plan

- One page-level heading and logical subheadings.
- Every input has a descriptive visible label; guidance precedes sensitive-looking simulation fields.
- Native Streamlit controls are preferred for keyboard behavior.
- Contrast is checked for text, controls, focus, badges, and error states.
- Status always combines text/icon/color.
- Product image descriptions communicate function, not decorative detail.
- Errors identify the field, problem, and correction; validation summary receives prominent placement.
- Tap targets and layouts remain usable near 320–375 px viewport widths.
- Tables/charts have textual summaries; no essential information appears only on hover.
- Price, dates, ratings, and order statuses use readable formats.
- Automated lint/smoke checks supplement, but do not replace, manual keyboard, contrast, zoom, and mobile review.

## 21. Performance plan

- Keep dependencies to Streamlit plus development-only Pytest/Ruff unless a documented need emerges.
- Build indexes by product ID, category, SKU, and normalized search tokens once per loaded dataset.
- Cache immutable sample construction with data-version keys; never cache mutable cart/security state globally.
- Keep session state small and centralized behind typed helpers.
- Compute derived values in pure functions and avoid repeated file reads on rerun.
- Use compact local image assets with explicit dimensions and lazy display where Streamlit allows.
- Avoid remote fonts/images, APIs, trackers, and background jobs.
- Target fast cold startup to the no-data welcome screen and near-instant deterministic sample load.
- Profile before optimization; include catalogue/filter and scoring benchmarks only if later evidence warrants them.

## 22. Testing strategy

### Unit tests

- Model construction, invalid boundaries, enums, money/date serialization
- Product stock/sale rules and relationship validators
- Search normalization, combined filters, effective-price filtering, stable sorting
- Cart line changes, stock limits, subtotal/rounding
- Coupon eligibility, percentage/fixed caps, expiration, category rules
- Shipping eligibility/free threshold and total order of operations
- Checkout field validation, no-payment-data contract, idempotency, totals
- Order creation, valid status transitions, inventory updates, rollback on failure
- Wishlist uniqueness and move-to-cart
- Severity grouping, de-duplication, score formula/bands, no-applicable result
- Remediation prerequisites, verification, expected impact, quick-win ordering
- Snapshot comparison: resolved/new/regressed/unchanged and methodology mismatch
- Plugin update, abandoned, vulnerability-indicator, inactive, and excessive-count rules

### Integration tests

- In-memory repository use cases end to end
- JSON repository CRUD/round-trip and schema envelopes
- Atomic replacement and previous-good backup
- Corrupt/truncated/unknown-version files do not overwrite or partially load
- Explicit load/reset/persistence opt-in behavior
- Report schema, disclaimer, determinism, and privacy filtering

### Integrity, privacy, and offline tests

- Expected sample counts/mixes, unique identifiers, referential integrity, reconciled totals
- Reserved `.test` domains and absence of known personal strings
- Secret-pattern scan for API keys, passwords, tokens, cookies, card-like data, and `.env`
- No network client imports/runtime URLs; local assets all resolve
- Importing every project module in an empty temporary directory creates no files
- Basic application startup creates no data; sample load occurs only after explicit action

### UI and release tests

- Streamlit headless startup smoke test
- Navigation registry includes every planned destination once
- Key page rendering tests where Streamlit’s testing API is stable
- Checkout disclaimer and simulator notice visible
- Narrow-layout/manual mobile review, keyboard pass, contrast review
- Python/Streamlit version consistency across configuration and docs
- README feature/navigation/command/link consistency

Quality gates: `ruff check`, `ruff format --check`, full `pytest`, import-safety test, secret/privacy audit, and Streamlit smoke test. Coverage is used to find gaps, not as an artificial test-count target.

## 23. Security and privacy plan

- No secrets, credentials, tokens, cookies, real customer/order/payment records, or real administrator details.
- No `.env` requirement; `.gitignore` will exclude local writable demo state and common secret files.
- Input text is length-bounded and rendered through safe Streamlit primitives; unsafe HTML is avoided.
- JSON loads are schema-validated; filenames/paths are fixed or allowlisted; image paths must remain local.
- Reports are generated from allowlisted fields and prominently marked fictional.
- Checkout has no card number, CVV, bank account, password, or token model.
- Dependency versions receive review before release; minimal dependencies reduce supply-chain surface.
- Git history, repository files, screenshots, fixtures, generated reports, and deployment settings receive a final privacy/secrets audit.
- The release checklist searches for email/phone/address patterns, credential keywords, private keys, high-entropy tokens, browser artifacts, `.env`, and accidental user names.
- Documentation distinguishes demonstration recommendations from legal, compliance, or professional security advice.

## 24. Documentation plan

- **README.md:** Overview, demo/source links, features, architecture, methodology, setup, tests, screenshots, limitations, privacy, hosted persistence warning, and portfolio context.
- **PHASE_1_ARCHITECTURE.md:** This authoritative plan and decision record.
- **TESTING.md:** Test layers, commands, fixtures, manual checks, and CI gates.
- **SECURITY_METHODOLOGY.md:** Taxonomy, scoring, plugin/control logic, assumptions, and disclaimers.
- **DEPLOYMENT.md:** Streamlit Community Cloud setup, Python version, persistence limitation, smoke/rollback steps.
- **SCREENSHOTS.md:** Required views, fictional-data review, viewport sizes, alt text/captions, and refresh procedure.
- **RELEASE_CHECKLIST.md:** Quality, privacy, secrets, accessibility, links, version, deployment, and portfolio integration gates.

Architecture and methodology documents are updated in the same phase as relevant behavior changes.

## 25. Deployment plan

Deployment is forbidden until Phase 7. When authorized:

1. Complete release-candidate tests and audits.
2. Initialize the independent Git repository and create the GitHub repository.
3. Pin compatible minimal runtime dependencies and declare Python 3.12.
4. Verify headless startup locally and in CI.
5. Create Streamlit Community Cloud application from the independent repository.
6. Configure no secrets because the simulator requires none.
7. Verify cold start, explicit sample loading, all destinations, mobile layout, report download, disclaimers, and reset.
8. Document that filesystem persistence on hosted Streamlit may reset and is not suitable for real data.
9. Record production URL, tagged release, screenshots, and rollback path.

## 26. Portfolio integration plan

Also forbidden until Phase 7. When authorized:

- Locate and verify the existing portfolio repository and its deployment instructions.
- Find the single existing project entry whose title begins “WooCommerce Storefront & Security Hardening.”
- Update that entry only; fail safely if zero or multiple matches occur.
- Do not create a duplicate card.
- Preserve the existing image unless the user explicitly approves changing it.
- Add the verified Streamlit live URL and GitHub source URL.
- Test “Launch Live Demo” and “View Source” from the built/deployed portfolio.
- Use the portfolio’s existing Cloudflare Pages workflow.
- Review the exact diff to ensure PromiseAgricTech and all unrelated projects remain unchanged.

## 27. Seven-phase implementation roadmap

### Phase 1 — Architecture and specification

- **Goals:** Resolve identity, scope, models, scoring, storage, UX, testing, release plan.
- **Files:** `docs/PHASE_1_ARCHITECTURE.md` only.
- **Features:** None; planning only.
- **Tests:** Document review and file/scope audit only.
- **Complete when:** All 30 requested specification sections are covered and decisions are explicit.
- **Forbidden:** Application code, Git initialization, GitHub, deployment, portfolio edits.

### Phase 2 — Foundation, models, and validation

- **Goals:** Establish package/configuration; implement enums, models, validation, serialization contracts, deterministic sample fixtures.
- **Files:** `pyproject.toml`, requirements/config, domain and sample-data modules, foundational tests, minimal README status.
- **Features:** Domain construction and validated in-memory fixture loading; no full UI.
- **Tests:** Model/enum/serialization/sample integrity/import safety/privacy/offline checks.
- **Complete when:** All fixtures reconstruct cleanly, relationships/totals validate, imports cause no writes, quality gates pass.
- **Forbidden:** Persistence writes, storefront/security feature UI, Git/GitHub/deployment/portfolio changes.

### Phase 3 — Storage, repositories, and services

- **Goals:** In-memory/JSON repositories, atomic storage, corruption recovery, commerce and security service logic.
- **Files:** repository/storage/application modules and unit/integration tests.
- **Features:** Search/filter, cart/coupon/shipping/checkout core, scoring/remediation/comparison/report logic through service APIs.
- **Tests:** Repository round trips, atomicity/corruption, calculations, scoring, workflows, report/privacy contracts.
- **Complete when:** Use cases pass against in-memory repositories; opt-in JSON behavior is safe and deterministic.
- **Forbidden:** Polished full UI, Git/GitHub/deployment/portfolio changes.

### Phase 4 — Storefront experience

- **Goals:** Build responsive storefront workspace and complete simulated customer journey.
- **Files:** Streamlit shell/state/shared components and storefront views; local product assets; UI tests/docs updates.
- **Features:** Home, Shop/details, Cart & Checkout, My Store, Store Information.
- **Tests:** Navigation/render smoke, checkout disclaimer, idempotency, accessible validation, mobile/manual review.
- **Complete when:** A user can explicitly load data and finish a fictional order without sensitive input or inconsistent stock/totals.
- **Forbidden:** Claiming real commerce/authentication; GitHub/deployment/portfolio changes.

### Phase 5 — Security-hardening workspace

- **Goals:** Build posture, components, controls/findings, remediation, comparison, export.
- **Files:** security UI modules/components, methodology docs, expanded tests.
- **Features:** Five security destinations, score explanation, quick wins, before/after, JSON report/reset.
- **Tests:** UI/service integration, severity/status display, verification rules, methodology/disclaimer, export privacy.
- **Complete when:** Reviewers can trace each score change to fictional evidence and remediation without certification claims.
- **Forbidden:** Live scanning/connections; GitHub/deployment/portfolio changes.

### Phase 6 — Quality, documentation, and release candidate

- **Goals:** Polish UX/accessibility/performance; complete docs/assets; audit privacy, secrets, offline behavior, and versions.
- **Files:** Final README and docs, screenshot plan/assets, CI workflow definition, release checklist.
- **Features:** Robust empty/error/corruption states and release-ready presentation.
- **Tests:** Full automated suite, manual accessibility/mobile matrix, startup/offline/privacy/secrets/version/doc consistency checks.
- **Complete when:** Release checklist passes locally and no known high-priority defect remains.
- **Forbidden:** Git initialization, GitHub repository, live deployment, portfolio modification unless Phase 7 is separately authorized.

### Phase 7 — GitHub, deployment, screenshots, release, and portfolio integration

- **Goals:** Publish independent source, deploy Streamlit app, capture verified screenshots, update existing portfolio entry.
- **Files:** Git metadata, final workflow/release metadata, screenshot updates, narrowly scoped portfolio entry change.
- **Features:** Live demo/source links and production validation.
- **Tests:** CI, deployed smoke/navigation/mobile/report/disclaimer checks; link checks; portfolio build/deploy verification.
- **Complete when:** GitHub and Streamlit URLs work, release is tagged, existing portfolio card buttons work, unrelated projects are untouched.
- **Forbidden:** Creating duplicate portfolio entry, altering existing image without approval, modifying PromiseAgricTech/unrelated projects, adding secrets/real data.

## 28. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Simulator mistaken for live WooCommerce/security scanner | Persistent simulator labeling; clear README/UI/export disclaimers; avoid live-scan language |
| Fake precision or misleading score | Whole-number educational index plus band/counts; published weights; traceable changes; certification disclaimer |
| Duplicate risk from finding/control overlap | Linked-control de-duplication rule and dedicated tests |
| Streamlit reruns duplicate orders or lose state | Central session adapter, idempotency token, transactional service operation |
| Hosted filesystem resets | Session-first default, explicit opt-in persistence, prominent ephemeral-host warning |
| Corrupt JSON destroys state | Validate-before-replace, atomic writes, previous-good backup, no silent overwrite |
| Accidental personal/secret data | Reserved fictional domains, allowlisted export fields, automated pattern scans and final manual audit |
| Payment UI invites sensitive entry | No credential fields; strong pre-checkout warning; method labels explicitly simulated |
| Too many destinations | Five destinations per workspace; details grouped in tabs/context |
| Streamlit CSS/API brittleness | Prefer native controls; minimal CSS; smoke tests with pinned compatible version |
| Remote assets/privacy leakage | Local optimized assets only; offline-safety tests |
| Inventory/totals inconsistency | Decimal arithmetic, immutable order snapshot, validated transactional update/rollback |
| Accessibility regression | Text status labels, contrast/keyboard/mobile manual gates, chart alternatives |
| Portfolio collateral changes | Exact single-entry match, scoped diff, link/build tests, preserve image/unrelated projects |

## 29. Definition of done

### Phase 1 definition of done

- One standalone project folder exists at the approved path.
- This architecture document contains the 30 requested deliverables.
- Identity, disclaimer, navigation, models, validation, enums, relationships, workflows, scoring, persistence, architecture, UI, accessibility, performance, tests, privacy, docs, release, and integration plans are concrete.
- No application/runtime/configuration code exists.
- No sample working-data files exist.
- Git is not initialized.
- No repository, external service, deployment, or portfolio content is created or changed.

### Final product definition of done

- Both workspaces implement the approved scope with fictional deterministic data.
- All calculations and scoring are explainable and tested.
- Explicit data loading and opt-in persistence meet side-effect/corruption requirements.
- Application operates offline with local assets and no secrets or sensitive fields.
- Automated quality gates and manual accessibility/mobile/privacy checks pass.
- Documentation accurately describes behavior and hosted limitations.
- Only after Phase 7 authorization: independent GitHub source, working Streamlit deployment, release evidence, and existing portfolio entry links are verified.

## 30. Recommended next-phase prompt outline

When ready, explicitly authorize **Phase 2 only** and request:

1. Confirm this architecture or list approved changes.
2. Create the minimal Python 3.12 project foundation at the exact standalone path.
3. Implement domain enums/models, validation, serializers, deterministic sample-data factory, and integrity checks only.
4. Add Pytest and Ruff configuration with focused Phase 2 tests.
5. Preserve import/startup side-effect rules and do not write sample data.
6. Create no complete Streamlit experience beyond any minimal non-functional entry-point decision explicitly approved.
7. Do not initialize Git, create GitHub resources, deploy, or modify the portfolio.
8. Report files, test results, assumptions, and any architecture deviations; stop before Phase 3.

### Decisions to approve before or during Phase 2

- Confirm the fictional store name **Northstar Desk & Living**.
- Confirm that default operation is session-only and local JSON persistence is a separate explicit opt-in.
- Confirm the transparent de-duplicated scoring weights/bands.
- Confirm product imagery will use locally created neutral illustrations/placeholders rather than product photography.
- Confirm whether the eventual open-source license should be MIT (decision can wait until Phase 6/7).

