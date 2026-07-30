# Phase 7 Deployment Plan

No deployment is performed in Phase 6.

## Target

- Platform: Streamlit Community Cloud
- Branch: `main`
- Main file: `app.py`
- Python: 3.12
- Secrets: empty / none required

## Required repository state

- Independent Git repository initialized only after Phase 7 approval.
- Verified GitHub source repository with the release-candidate tree.
- Quality workflow green on `main`.
- `pyproject.toml` committed with Streamlit runtime and development extras.
- No `.streamlit/secrets.toml`, working JSON, backup, cache, browser, or temporary
  screenshot artifacts.
- Release-readiness checks complete except explicitly Phase-7-only items.

## Deployment steps

1. Create the independent GitHub repository and push the approved `main`.
2. Confirm quality checks pass on Python 3.12.
3. Create the Streamlit Community Cloud app from that repository/branch.
4. Set the main file to `app.py`.
5. Configure Python 3.12 and no secrets.
6. Deploy and wait for a terminal healthy state.
7. Open the production URL in a clean browser session.

## Expected sample-data behavior

The deployed app opens empty. No fixture or persistence file is created automatically.
The visitor must select **Load Fictional Sample Data**. State is per session and may
reset on refresh, inactivity, restart, redeploy, or platform filesystem reset.

## Post-deployment verification

- Health and cold start.
- Empty Storefront and Security workspaces.
- Explicit sample load.
- All 16 destinations.
- Search/filters/sorting/product details.
- Cart, coupon, shipping, checkout warning, confirmation, inventory, history, wishlist.
- 35-before / 83-after Security summary.
- Components/findings/hardening.
- JSON download and privacy text.
- No sensitive inputs, network integrations, or browser console errors.
- 1440px, 768px, and 390px layouts plus keyboard/zoom checks.

## Screenshot capture

Capture only from the verified production URL after deployment. Use the exact filenames
in `docs/screenshots/README.md`; do not substitute mock or AI-generated screens. Review
every frame for fictional data and absence of browser/local personal information.

## Common failure checks

- Incorrect app path or branch.
- Unsupported Python/dependency resolution.
- Stale application version.
- Fixture not loaded because the explicit button was not used.
- Expected state reset mistaken for durable persistence.
- Blocked report download.
- Accidental secrets or working files committed.

## Rollback

Deploy a previously verified saved source revision. Do not edit production data because
the demo is session-first and non-durable.

