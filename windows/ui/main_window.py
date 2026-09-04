"""
CLIPBOARD LAN - Main Window
Rail d'icônes clair (boutons blancs individuels, icône active en carré
bleu marine) + zone de contenu sur fond bleu-gris pâle.

CHEMIN: windows/ui/main_window.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, font


class MainWindow(ctk.CTk):
    """Fenêtre principale de Clipboard LAN — thème clair."""

    def __init__(self, sync_manager=None):
        super().__init__()

        self.sync_manager = sync_manager

        self.title("Clipboard LAN")
        self.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.configure(fg_color=COLORS["background"])

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.panels = {}
        self.current_panel = None
        self.nav_buttons = {}

        self._create_layout()

    def _create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_rail()
        self._create_header()

        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=SPACING["lg"], pady=(0, SPACING["lg"]))

    def _create_rail(self):
        self.rail = ctk.CTkFrame(
            self, width=DIMENSIONS["rail_width"], fg_color=COLORS["rail"], corner_radius=0
        )
        self.rail.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.rail.grid_propagate(False)

        marks = [
            ("dashboard", "▤"),
            ("devices", "◫"),
            ("history", "≡"),
            ("settings", "⚙"),
        ]

        for i, (key, mark) in enumerate(marks):
            btn = ctk.CTkButton(
                self.rail, text=mark, font=("Segoe UI", 18),
                width=48, height=48, corner_radius=RADIUS["md"],
                fg_color=COLORS["rail_icon_bg"], hover_color=COLORS["rail_icon_bg_hover"],
                text_color=COLORS["rail_icon"], border_width=1, border_color=COLORS["border"],
                command=lambda k=key: self.show_panel(k)
            )
            btn.grid(row=i, column=0, padx=14, pady=(28 if i == 0 else 10, 10))
            self.nav_buttons[key] = btn

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0, height=64)
        header.grid(row=0, column=1, sticky="nsew", padx=SPACING["lg"], pady=(SPACING["md"], 0))
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header, text="Clipboard LAN",
            font=font("lg", "bold"), text_color=COLORS["text_primary"]
        )
        title.pack(side="left", anchor="w")

        status_pill = ctk.CTkFrame(header, fg_color=COLORS["card"], corner_radius=RADIUS["full"],
                                    border_width=1, border_color=COLORS["border"], height=32)
        status_pill.pack(side="right")

        self.status_dot = ctk.CTkLabel(status_pill, text="●", font=("Segoe UI", 11), text_color=COLORS["success"])
        self.status_dot.pack(side="left", padx=(12, 4), pady=6)

        self.status_label = ctk.CTkLabel(
            status_pill, text="192.168.1.50:7777",
            font=font("xs", mono=True), text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left", padx=(0, 14), pady=6)

    def set_connection_status(self, connected: bool, address: str = ""):
        self.status_dot.configure(text_color=COLORS["success"] if connected else COLORS["offline"])
        state = "" if connected else "Hors ligne "
        self.status_label.configure(text=f"{state}{address}")

    def register_panel(self, name: str, panel_widget):
        self.panels[name] = panel_widget

    def show_panel(self, name: str):
        if self.current_panel and self.current_panel in self.panels:
            self.panels[self.current_panel].pack_forget()

        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=COLORS["rail_active_bg"], text_color=COLORS["rail_active_icon"],
                              border_width=0)
            else:
                btn.configure(fg_color=COLORS["rail_icon_bg"], text_color=COLORS["rail_icon"],
                              border_width=1, border_color=COLORS["border"])

        if name in self.panels:
            self.panels[name].pack(fill="both", expand=True)
            self.current_panel = name

    def get_content_frame(self):
        return self.content_frame

    def run(self):
        self.mainloop()


def create_main_window(sync_manager=None) -> MainWindow:
    return MainWindow(sync_manager=sync_manager)


if __name__ == "__main__":
    app = MainWindow()
    app.run()