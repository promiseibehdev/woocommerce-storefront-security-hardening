from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


def _free_loopback_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _working_artifacts() -> set[Path]:
    patterns = (
        "state.json",
        "commerce_state.json",
        "security_state.json",
        "*.corrupt.*.json",
    )
    return {path for pattern in patterns for path in PROJECT_ROOT.rglob(pattern)} | set(
        PROJECT_ROOT.rglob("backups")
    )


def test_bounded_streamlit_process_health_and_clean_shutdown(tmp_path: Path) -> None:
    port = _free_loopback_port()
    before = _working_artifacts()
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
            "STREAMLIT_SERVER_HEADLESS": "true",
        }
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(PROJECT_ROOT / "app.py"),
            "--server.address",
            "127.0.0.1",
            "--server.port",
            str(port),
            "--server.fileWatcherType",
            "none",
        ],
        cwd=tmp_path,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    healthy = False
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/_stcore/health",
                    timeout=1,
                ) as response:
                    healthy = response.status == 200 and response.read().strip() == b"ok"
                    if healthy:
                        break
            except OSError:
                time.sleep(0.2)
        assert healthy, process.stdout.read() if process.poll() is not None else "health timeout"
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    assert process.poll() is not None
    assert _working_artifacts() == before
