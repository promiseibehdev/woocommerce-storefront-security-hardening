from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from woo_security_simulator.metadata import (
    APPLICATION_VERSION,
    DOMAIN_SCHEMA_VERSION,
)
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.sample_data import build_sample_state
from woo_security_simulator.services.report import SecurityReportService
from woo_security_simulator.ui.pages import PAGES
from woo_security_simulator.ui.security_pages import SECURITY_PAGES

PROJECT_ROOT = Path(__file__).parents[1]
CURRENT_DOCS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "ARCHITECTURE.md",
    PROJECT_ROOT / "docs" / "TESTING.md",
    PROJECT_ROOT / "docs" / "SECURITY_METHODOLOGY.md",
    PROJECT_ROOT / "docs" / "DEPLOYMENT.md",
    PROJECT_ROOT / "docs" / "RELEASE_READINESS.md",
)


def test_release_version_schema_and_python_are_consistent() -> None:
    configuration = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert configuration["project"]["version"] == APPLICATION_VERSION == "1.0.0"
    assert configuration["project"]["requires-python"] == ">=3.12"
    assert DOMAIN_SCHEMA_VERSION == 1
    for path in CURRENT_DOCS:
        text = path.read_text(encoding="utf-8")
        if path.name in {"README.md", "RELEASE_READINESS.md"}:
            assert "1.0.0" in text


def test_no_stale_development_versions_outside_historical_phase_docs() -> None:
    stale = re.compile(r"\b0\.(?:2|3|4|5)\.0\b")
    violations = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.name.startswith("PHASE_"):
            continue
        if path.suffix.lower() not in {".py", ".toml", ".md", ".yml", ".yaml"}:
            continue
        if stale.search(path.read_text(encoding="utf-8")):
            violations.append(path.relative_to(PROJECT_ROOT))
    assert violations == []


def test_runtime_dependency_and_license_are_release_ready() -> None:
    configuration = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert configuration["project"]["dependencies"] == ["streamlit>=1.58,<2"]
    assert set(configuration["project"]["optional-dependencies"]["dev"]) == {
        "pytest>=8.3,<9",
        "ruff>=0.16,<0.17",
    }
    assert configuration["project"]["license"]["text"] == "MIT"
    assert (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")


def test_final_navigation_count_and_labels() -> None:
    assert tuple(PAGES) == (
        "Store Home",
        "Shop",
        "Categories",
        "Product Details",
        "Shopping Cart",
        "Checkout",
        "Order Confirmation",
        "My Account",
        "Order History",
        "Wishlist",
        "Store Information",
    )
    assert tuple(SECURITY_PAGES) == (
        "Security Overview",
        "Components",
        "Findings",
        "Hardening",
        "Reports",
    )
    assert len(PAGES) + len(SECURITY_PAGES) == 16


def test_report_and_fixture_privacy_release_audit() -> None:
    state = build_sample_state()
    report = SecurityReportService(UnitOfWork(state)).generate(
        audited_at=state.audit_snapshots[-1].captured_at
    )
    payload = json.loads(report)
    assert payload["privacy_statement"]
    assert all(customer.email.endswith("@example.test") for customer in state.customers)
    assert all(account.email.endswith("@example.test") for account in state.user_accounts)
    assert state.site_profile is not None
    assert state.site_profile.base_url_label.endswith(".test")
    for forbidden in (
        "C:\\Users\\",
        "/Users/",
        "api_key",
        "access_token",
        "card_number",
        "cvv",
        "browser_cookie",
    ):
        assert forbidden.casefold() not in report.casefold()


def test_publication_links_screenshots_and_required_files() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "[PHASE_7_" not in readme
    assert (
        "https://woocommerce-storefront-security-hardening-p9d7t7mkrclous9etglr.streamlit.app/"
    ) in readme
    assert "https://github.com/promiseibehdev/woocommerce-storefront-security-hardening" in readme
    required = (
        "docs/ARCHITECTURE.md",
        "docs/TESTING.md",
        "docs/SECURITY_METHODOLOGY.md",
        "docs/DEPLOYMENT.md",
        "docs/QUALITY_AUDIT.md",
        "docs/RELEASE_READINESS.md",
        "docs/screenshots/README.md",
        ".github/workflows/quality.yml",
        ".gitignore",
        "LICENSE",
        "docs/screenshots/store-home.png",
        "docs/screenshots/shop.png",
        "docs/screenshots/product-details.png",
        "docs/screenshots/checkout.png",
        "docs/screenshots/security-overview.png",
        "docs/screenshots/components.png",
        "docs/screenshots/findings.png",
        "docs/screenshots/hardening.png",
        "docs/screenshots/reports.png",
    )
    assert all((PROJECT_ROOT / relative).is_file() for relative in required)


def test_workflow_is_quality_only_and_hygiene_covers_generated_data() -> None:
    workflow = (PROJECT_ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.12"' in workflow
    assert "ruff check ." in workflow
    assert "ruff format --check ." in workflow
    assert "python -m pytest" in workflow
    assert "deploy" not in workflow.casefold()
    assert "secrets." not in workflow.casefold()
    ignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (
        "__pycache__/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".venv/",
        ".demo_data/",
        "backups/",
        ".streamlit/secrets.toml",
        "playwright-report/",
    ):
        assert pattern in ignore
