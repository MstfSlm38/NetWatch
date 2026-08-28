"""NetWatch application entry point."""

from __future__ import annotations

import threading

import customtkinter as ctk

from network.monitor import collect_network_info


class NetWatchApp(ctk.CTk):
    """Main NetWatch application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("NetWatch")
        self.geometry("760x480")
        self.minsize(680, 420)

        self.status_value: ctk.CTkLabel | None = None
        self.ip_value: ctk.CTkLabel | None = None
        self.hostname_value: ctk.CTkLabel | None = None
        self.ping_value: ctk.CTkLabel | None = None
        self.status_badge: ctk.CTkLabel | None = None

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            sidebar, text="NetWatch", font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=24, pady=(28, 4))
        ctk.CTkLabel(sidebar, text="Network Monitor", text_color="gray").grid(
            row=1, column=0, padx=24, pady=(0, 28)
        )
        ctk.CTkButton(sidebar, text="Dashboard", command=self.refresh).grid(
            row=2, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Refresh", command=self.refresh).grid(
            row=3, column=0, padx=18, pady=8, sticky="ew"
        )

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=1, padx=28, pady=(24, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="Network Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        self.status_badge = ctk.CTkLabel(
            header, text="Checking...", corner_radius=16, padx=14, pady=6
        )
        self.status_badge.grid(row=0, column=1, sticky="e")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=1, padx=28, pady=(8, 28), sticky="nsew")
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure((0, 1), weight=1)

        self.status_value = self._create_card(content, "Connection", 0, 0)
        self.ping_value = self._create_card(content, "Ping", 0, 1)
        self.ip_value = self._create_card(content, "Local IP", 1, 0)
        self.hostname_value = self._create_card(content, "Hostname", 1, 1)

    def _create_card(
        self, parent: ctk.CTkFrame, title: str, row: int, column: int
    ) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, text_color="gray").pack(
            anchor="w", padx=20, pady=(20, 4)
        )
        value = ctk.CTkLabel(
            card, text="Checking...", font=ctk.CTkFont(size=22, weight="bold")
        )
        value.pack(anchor="w", padx=20, pady=(0, 20))
        return value

    def refresh(self) -> None:
        for label in (
            self.status_badge,
            self.status_value,
            self.ip_value,
            self.hostname_value,
            self.ping_value,
        ):
            if label is not None:
                label.configure(text="Checking...")
        threading.Thread(target=self._collect_network_info, daemon=True).start()

    def _collect_network_info(self) -> None:
        info = collect_network_info()
        self.after(0, lambda: self._update_ui(info))

    def _update_ui(self, info) -> None:
        status = "Online" if info.connected else "Offline"
        self.status_value.configure(text=status)
        self.ip_value.configure(text=info.local_ip)
        self.hostname_value.configure(text=info.hostname)
        self.ping_value.configure(text=info.ping)
        self.status_badge.configure(text=status)


def main() -> None:
    """Start NetWatch."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = NetWatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
