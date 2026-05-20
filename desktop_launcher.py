"""
Desktop launcher — wraps the FastAPI app inside a native pywebview window.

Usage:
    python launcher.py
"""

import subprocess
import sys
import threading
import time

import webview  # pip install pywebview

_PORT = 8000
_URL = f"http://localhost:{_PORT}"


def _start_fastapi() -> None:
    """Start the FastAPI/uvicorn server as a background subprocess."""
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host=127.0.0.1",
            f"--port={_PORT}",
            "--no-access-log",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_server(timeout: int = 15) -> bool:
    """Poll until Streamlit is responding or timeout is reached."""
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(_URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    t = threading.Thread(target=_start_fastapi, daemon=True)
    t.start()

    print("Waiting for FastAPI to start...")
    if not _wait_for_server():
        print("WARNING: Server did not respond in time - opening anyway.")

    window = webview.create_window(
        title="3D Print Manager",
        url=_URL,
        width=1440,
        height=920,
        resizable=True,
        min_size=(900, 600),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
