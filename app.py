"""Streamlit entry point for the Phase 4 fictional storefront."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from woo_security_simulator.ui.shell import run_storefront  # noqa: E402

run_storefront()
