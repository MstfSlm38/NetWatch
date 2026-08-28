"""Network monitoring and diagnostic utilities."""

from __future__ import annotations

import platform
import socket
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkInfo:
    """Collected network information."""

    connected: bool
    local_ip: str
    hostname: str
    ping: str


def get_local_ip() -> str:
    """Return the local IPv4 address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("1.1.1.1", 80))
            return sock.getsockname()[0]
    except OSError:
        return "Unavailable"


def get_hostname() -> str:
    """Return the current computer hostname."""
    try:
        return socket.gethostname()
    except OSError:
        return "Unavailable"


def check_connection() -> bool:
    """Check whether the device can reach the internet."""
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=2):
            return True
    except OSError:
        return False


def run_ping(host: str = "1.1.1.1") -> str:
    """Ping a host and return a short human-readable result."""
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", "2000", host]
    else:
        command = ["ping", "-c", "1", "-W", "2", host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )

        if result.returncode != 0:
            return "Failed"

        output = result.stdout

        if "time=" in output:
            value = output.split("time=", 1)[1].split("ms", 1)[0]
            return f"{value.strip()} ms"

        if "time<" in output:
            value = output.split("time<", 1)[1].split(" ms", 1)[0]
            return f"<{value.strip()} ms"

        return "Success"
    except (OSError, subprocess.SubprocessError):
        return "Failed"


def collect_network_info(host: str = "1.1.1.1") -> NetworkInfo:
    """Collect the network information shown by the dashboard."""
    return NetworkInfo(
        connected=check_connection(),
        local_ip=get_local_ip(),
        hostname=get_hostname(),
        ping=run_ping(host),
    )
