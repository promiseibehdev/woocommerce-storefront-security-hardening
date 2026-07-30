# Phase 4 — Streamlit Storefront

## Scope

Phase 4 adds only the customer-facing fictional storefront. The Security workspace,
deployment, GitHub, Git initialization, analytics, external APIs, authentication, and
portfolio integration remain absent.

## Navigation

The sidebar groups eleven destinations:

- Browse: Store Home, Shop, Categories, Product Details
- Purchase: Shopping Cart, Checkout, Order Confirmation
- My Store: My Account, Order History, Wishlist
- Information: Store Information

The “Fictional customer view” selector changes demonstration context only. It is not
authentication or authorization.

## Empty state and sample loading

`ApplicationStateService` is created per Streamlit session and begins with the valid
empty aggregate. The application does not call the sample factory automatically. Until
the user selects **Load Fictional Sample Data**, catalogue destinations show a clear
empty state and no cart is created.

The explicit load action builds the deterministic Northstar fixture in memory. It does
not write a file or create a backup directory.

## Presentation boundaries

The UI calls the existing Phase 3 services:

- `CatalogueService` for listing, search, filters, sorting, availability, related items,
  and summary counts.
- `CartService` for cart mutations, stock validation, subtotal, coupon, shipping, and
  total calculations.
- `CheckoutService` for transaction-like order creation, inventory updates, cart
  clearing, and activity recording.
- `AccountService` for profile, history, order, status, and wishlist behavior.

No calculation or commerce rule is reimplemented in Streamlit.

## Checkout safety

Checkout displays:

> Simulation only. No real payment is processed.

The form only selects existing fictional customer addresses, shipping methods, and
simulated payment methods. It contains no card-number, CVV, banking-credential, or real
address fields. Confirmation repeats the simulation warning.

## Responsive and accessible design

- Wide layouts use Streamlit columns that collapse at narrow widths.
- A mobile CSS breakpoint reduces page padding, heading size, and product artwork height.
- Inputs have visible labels and contextual help.
- Validation errors explain the correction rather than exposing exceptions.
- Stock state uses an icon plus text; information is not color-only.
- Buttons use descriptive labels and full-width layouts where practical.
- Product imagery uses a local abstract placeholder with an accessibility-hidden
  decorative marker; there is no remote image dependency.
- Heading hierarchy, bordered groups, empty states, and high-contrast neutral styling
  support scanability.

## Testing

Streamlit’s application testing API verifies empty startup, the explicit load action,
all eleven destinations, cart creation and quantity controls, sensitive-field absence,
the required checkout warning, simulated order placement, and confirmation.

The full domain, storage, repository, service, import-safety, offline-safety, and privacy
suite remains active.

## Phase 5 guidance

Phase 5 may add the approved Security workspace to the same application shell. It should
reuse the existing risk, scoring, finding, remediation, comparison, activity, and report
services; preserve per-session state; and add grouped Security navigation without
duplicating security calculations in Streamlit.

