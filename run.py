r"""Reliable single-command launcher for AgriCast AI on Windows/macOS/Linux.

Run with the project virtual environment:
    .venv\Scripts\python.exe run.py   (Windows PowerShell)
    .venv/bin/python run.py              (macOS/Linux)

Starts FastAPI and Streamlit, checks both services, logs API output, and shuts
both child processes down on Ctrl+C. Startup failure in either service is fatal.
"""
from __future__ import annotations

import importlib.util
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
API_HOST = "127.0.0.1"
API_PORT = 8000
UI_HOST = "127.0.0.1"
UI_PORT = 8501
STARTUP_TIMEOUT_SECONDS = 25.0
POLL_INTERVAL_SECONDS = 0.25
LOG_DIR = ROOT / "data" / "logs"


def check_dependencies() -> list[str]:
    """Return required Python modules that cannot be imported."""
    required = ("streamlit", "fastapi", "uvicorn", "sklearn", "pandas", "numpy", "plotly", "mcp")
    return [name for name in required if importlib.util.find_spec(name) is None]


def port_is_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def stop_process(proc: subprocess.Popen | None, name: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    print(f"Stopping {name}...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print(f"{name} did not stop in time; forcing shutdown.")
        proc.kill()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print(f"WARNING: unable to confirm {name} shutdown.")


def wait_for_http(url: str, proc: subprocess.Popen, name: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    last_error = "no response yet"
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            print(f"ERROR: {name} exited during startup (exit code {proc.returncode}).")
            return False
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if 200 <= response.status < 300:
                    return True
                last_error = f"HTTP {response.status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
        time.sleep(POLL_INTERVAL_SECONDS)
    print(f"ERROR: {name} did not become ready within {timeout:.0f}s. Last check: {last_error}")
    return False


def main() -> int:
    os.chdir(ROOT)
    print("AgriCast AI launcher")
    print(f"Project folder: {ROOT}")

    missing = check_dependencies()
    if missing:
        print("ERROR: Required dependencies are missing: " + ", ".join(missing))
        print("Install them with:")
        print(f'  "{sys.executable}" -m pip install -r requirements.txt')
        return 2

    for host, port, label in ((API_HOST, API_PORT, "FastAPI"), (UI_HOST, UI_PORT, "Streamlit")):
        if not port_is_available(host, port):
            print(f"ERROR: {label} port {port} is already in use at {host}:{port}.")
            print("Close the existing process or change the configured port before restarting.")
            return 3

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    api_log_path = LOG_DIR / "api.log"
    api_log = api_log_path.open("w", encoding="utf-8", buffering=1)
    api: subprocess.Popen | None = None
    ui: subprocess.Popen | None = None
    try:
        api_cmd: Sequence[str] = [
            sys.executable, "-m", "uvicorn", "agricast.api.main:app",
            "--host", API_HOST, "--port", str(API_PORT), "--log-level", "info",
        ]
        print(f"Starting FastAPI; log: {api_log_path}")
        api = subprocess.Popen(api_cmd, cwd=ROOT, stdout=api_log, stderr=subprocess.STDOUT)
        health_url = f"http://{API_HOST}:{API_PORT}/health"
        if not wait_for_http(health_url, api, "FastAPI", STARTUP_TIMEOUT_SECONDS):
            print(f"Inspect API startup details in: {api_log_path}")
            return 4
        print(f"OK: FastAPI health check passed: {health_url}")

        ui_cmd: Sequence[str] = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.address", UI_HOST, "--server.port", str(UI_PORT),
            "--server.headless", "true",
        ]
        print(f"Starting Streamlit at http://{UI_HOST}:{UI_PORT}")
        ui = subprocess.Popen(ui_cmd, cwd=ROOT)
        # Streamlit's health endpoint is more reliable than trusting its console banner.
        ui_health = f"http://{UI_HOST}:{UI_PORT}/_stcore/health"
        if not wait_for_http(ui_health, ui, "Streamlit", STARTUP_TIMEOUT_SECONDS):
            print("Streamlit failed to become ready. Check the error printed above.")
            return 5
        print("OK: Streamlit health check passed.")
        print("Both services are ready. Press Ctrl+C in this terminal to stop both.")

        while True:
            if api.poll() is not None:
                print(f"ERROR: FastAPI stopped unexpectedly (exit code {api.returncode}). See {api_log_path}")
                return 6
            if ui.poll() is not None:
                print(f"ERROR: Streamlit stopped unexpectedly (exit code {ui.returncode}).")
                return 7
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutdown requested (Ctrl+C).")
        return 130
    finally:
        stop_process(ui, "Streamlit")
        stop_process(api, "FastAPI")
        api_log.close()
        print("AgriCast AI launcher stopped.")


if __name__ == "__main__":
    raise SystemExit(main())
