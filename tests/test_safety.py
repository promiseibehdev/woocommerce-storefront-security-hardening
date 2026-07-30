from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).parents[1] / "src" / "woo_security_simulator"
NETWORK_MODULES = {
    "aiohttp",
    "ftplib",
    "http.client",
    "httpx",
    "requests",
    "socket",
    "telnetlib",
    "urllib.request",
    "websockets",
}


def test_importing_all_modules_creates_no_files(tmp_path: Path) -> None:
    modules = [
        ".".join(path.relative_to(PACKAGE.parent).with_suffix("").parts)
        for path in PACKAGE.rglob("*.py")
        if path.name != "__init__.py"
    ]
    script = (
        "import importlib, sys\n"
        f"sys.path.insert(0, {str(PACKAGE.parent)!r})\n"
        f"modules = {modules!r}\n"
        "for name in modules:\n"
        "    importlib.import_module(name)\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert list(tmp_path.iterdir()) == []


def test_source_has_no_network_capability_imports() -> None:
    violations: list[str] = []
    for path in PACKAGE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if any(
                    name == blocked or name.startswith(f"{blocked}.") for blocked in NETWORK_MODULES
                ):
                    violations.append(f"{path.name}: {name}")
    assert violations == []


def test_source_contains_no_runtime_http_endpoints() -> None:
    violations = []
    for path in PACKAGE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value.startswith(("http://", "https://"))
                and node.value not in {"http://", "https://"}
                and ".test" not in node.value
            ):
                violations.append(f"{path.name}: {node.value}")
    assert violations == []


def test_no_duplicate_security_ui_directory_exists() -> None:
    root = PACKAGE.parents[1]
    assert not (root / "src/woo_security_simulator/ui/security").exists()
