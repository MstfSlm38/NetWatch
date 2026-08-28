"""NetWatch application entry point."""

from __future__ import annotations

import socket
import subprocess
import platform
import threading
from dataclasses import dataclass

import customtkinter as ctk


@dataclass
class NetworkInfo:
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
    """Ping a host and return a short result."""
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

        # Windows usually reports "time=XXms".
        if "time=" in output:
            value = output.split("time=", 1)[1].split("ms", 1)[0]
            return f"{value.strip()} ms"

        # Some systems use "time<XX ms".
        if "time<" in output:
            value = output.split("time<", 1)[1].split(" ms", 1)[0]
            return f"<{value.strip()} ms"

        return "Success"

    except (OSError, subprocess.SubprocessError):
        return "Failed"


class NetWatchApp(ctk.CTk):
    """Main NetWatch application window."""

    def __init__(self) -> None:
        super().__init__()

        self.title("NetWatch")
        self.geometry("760x480")
        self.minsize(680, 420)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.status_value = None
        self.ip_value = None
        self.hostname_value = None
        self.ping_value = None

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Build the application interface."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(
            sidebar,
            text="NetWatch",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, padx=24, pady=(28, 4))

        subtitle = ctk.CTkLabel(
            sidebar,
            text="Network Monitor",
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 28))

        dashboard = ctk.CTkButton(
            sidebar,
            text="Dashboard",
            command=self.refresh,
        )
        dashboard.grid(row=2, column=0, padx=18, pady=8, sticky="ew")

        refresh = ctk.CTkButton(
            sidebar,
            text="Refresh",
            command=self.refresh,
        )
        refresh.grid(row=3, column=0, padx=18, pady=8, sticky="ew")

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=1, padx=28, pady=(24, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            header,
            text="Network Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w")

        self.status_badge = ctk.CTkLabel(
            header,
            text="Checking...",
            corner_radius=16,
            padx=14,
            pady=6,
        )
        self.status_badge.grid(row=0, column=1, sticky="e")

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(
            row=1,
            column=1,
            padx=28,
            pady=(8, 28),
            sticky="nsew",
        )

        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        self.status_value = self._create_card(
            content,
            "Connection",
            "Checking...",
            0,
            0,
        )

        self.ping_value = self._create_card(
            content,
            "Ping",
            "Checking...",
            0,
            1,
        )

        self.ip_value = self._create_card(
            content,
            "Local IP",
            "Checking...",
            1,
            0,
        )

        self.hostname_value = self._create_card(
            content,
            "Hostname",
            "Checking...",
            1,
            1,
        )

    def _create_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        value: str,
        row: int,
        column: int,
    ) -> ctk.CTkLabel:
        """Create a dashboard information card."""
        card = ctk.CTkFrame(parent)
        card.grid(
            row=row,
            column=column,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        label = ctk.CTkLabel(
            card,
            text=title,
            text_color="gray",
            font=ctk.CTkFont(size=14),
        )
        label.pack(anchor="w", padx=20, pady=(20, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        value_label.pack(anchor="w", padx=20, pady=(0, 20))

        return value_label

    def refresh(self) -> None:
        """Refresh network information without freezing the UI."""
        self.status_badge.configure(text="Checking...")
        self.status_value.configure(text="Checking...")
        self.ip_value.configure(text="Checking...")
        self.hostname_value.configure(text="Checking...")
        self.ping_value.configure(text="Checking...")

        threading.Thread(
            target=self._collect_network_info,
            daemon=True,
        ).start()

    def _collect_network_info(self) -> None:
        """Collect network information in the background."""
        connected = check_connection()
        local_ip = get_local_ip()
        hostname = get_hostname()
        ping = run_ping()

        info = NetworkInfo(
            connected=connected,
            local_ip=local_ip,
            hostname=hostname,
            ping=ping,
        )

        self.after(0, lambda: self._update_ui(info))

    def _update_ui(self, info: NetworkInfo) -> None:
        """Update the dashboard with collected information."""
        if info.connected:
            status = "Online"
        else:
            status = "Offline"

        self.status_value.configure(text=status)
        self.ip_value.configure(text=info.local_ip)
        self.hostname_value.configure(text=info.hostname)
        self.ping_value.configure(text=info.ping)
        self.status_badge.configure(text=status)


def main() -> None:
    """Start NetWatch."""
    app = NetWatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()