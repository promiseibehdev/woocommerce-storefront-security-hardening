# Testing

## Organization

- `test_*_models.py`: construction invariants and closed enums.
- `test_serialization.py`: strict typed round trips and rejected input.
- `test_sample_data.py`: deterministic counts, integrity, privacy, and relationships.
- `test_repositories.py`: CRUD, ordering, conflicts, isolation, and snapshots.
- `test_storage.py`: schema envelope, atomic failure, corruption, backup, retention,
  restore, and migration guard.
- `test_*_services.py`: commerce, checkout, activity, scoring, remediation, comparison,
  and report behavior.
- `test_storefront_ui.py` / `test_security_ui.py`: Streamlit interaction and navigation.
- `test_safety.py`: import/offline/file-creation boundaries.
- `test_release_readiness.py`: version, privacy, secrets, docs, dependencies, and hygiene.
- `test_startup_smoke.py`: bounded real Streamlit process and health endpoint.

## Commands

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

For a no-cache release verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -p no:cacheprovider
python -m ruff check --no-cache .
python -m ruff format --check --no-cache .
```

## Test layers

### Unit tests

Pure validation, serialization, calculations, filters, status transitions, risk scoring,
and summaries run without Streamlit or filesystem state.

### Integration tests

Unit-of-work/service flows verify checkout rollback, inventory updates, report generation,
atomic storage, and backup/recovery.

### Streamlit interaction tests

Streamlit `AppTest` creates independent sessions and verifies empty startup, explicit
fixture loading, all 16 destinations, filters, cart/checkout, security summaries, and
JSON download presence.

### Safety and privacy tests

AST/source/data/report checks reject network capability, external runtime URLs, unsafe
paths, non-reserved fixture identities, credential-like data, working files on import,
and stale release versions.

### Startup smoke test

A bounded subprocess launches `streamlit run app.py` on loopback with headless mode and
an isolated configuration directory. The test polls `/_stcore/health`, verifies no
project working/backup files appeared, and terminates the process in `finally`.

## Expected release-candidate result

Every test must pass with no warning suppression or weakened assertion. Ruff lint and
format checks must also pass.

## Manual accessibility/responsive checks for Phase 7

Automated tests cannot establish formal WCAG conformance. Before release, manually test:

- Keyboard-only navigation and visible focus.
- Browser zoom at 200%.
- Screen-reader labels/reading order for filters and checkout.
- Contrast using a recognized checker.
- 1440px desktop, 768px tablet, and 390px mobile widths.
- Sidebar/workspace switcher, grids, cards, details, cart, checkout, confirmation,
  score cards, tabs, findings, remediation, and report download.

Record results in `docs/RELEASE_READINESS.md`.

## Phase 7 CI plan

The quality workflow uses Python 3.12 on push and pull request, installs `.[dev]`, and
runs Ruff lint, Ruff format, the full test suite, and focused safety/startup checks. It
performs no deployment and requires no secrets.

