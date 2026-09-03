"""
CLIPBOARD LAN - Main Window
Rail de navigation intégré + en-tête avec pastille de statut réseau

CHEMIN: windows/ui/main_window.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, NAV_LABELS, font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, NAV_LABELS, font


class MainWindow(ctk.CTk):
    """
    Fenêtre principale de Clipboard LAN.

    Structure: rail d'icônes fin (intégré au fond) → header avec statut
    réseau en direct → zone de contenu (panels).
    """

    def __init__(self, sync_manager=None):
        super().__init__()

        self.sync_manager = sync_manager

        self.title("Clipboard LAN")
        self.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.configure(fg_color=COLORS["background"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

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
        """Rail d'icônes fin, séparé par un simple trait — pas un îlot coloré."""
        self.rail = ctk.CTkFrame(
            self, width=DIMENSIONS["rail_width"], fg_color=COLORS["rail"],
            corner_radius=0, border_width=0
        )
        self.rail.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.rail.grid_propagate(False)

        # Trait de séparation vertical
        sep = ctk.CTkFrame(self.rail, width=1, fg_color=COLORS["border"])
        sep.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        marks = [
            ("dashboard", "▤"),
            ("devices", "◫"),
            ("history", "≡"),
            ("settings", "⚙"),
        ]

        for i, (key, mark) in enumerate(marks):
            btn = ctk.CTkButton(
                self.rail, text=mark, font=("Segoe UI", 18),
                width=40, height=40, corner_radius=RADIUS["md"],
                fg_color="transparent", hover_color=COLORS["surface_hover"],
                text_color=COLORS["rail_icon"],
                command=lambda k=key: self.show_panel(k)
            )
            btn.grid(row=i, column=0, padx=12, pady=(24 if i == 0 else 8, 8))
            self.nav_buttons[key] = btn

    def _create_header(self):
        """En-tête: nom de l'app + pastille de statut réseau en direct."""
        header = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0, height=64)
        header.grid(row=0, column=1, sticky="nsew", padx=SPACING["lg"], pady=(SPACING["md"], 0))
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header, text="Clipboard LAN",
            font=font("lg", "bold"), text_color=COLORS["text_primary"]
        )
        title.pack(side="left", anchor="w")

        self.status_dot = ctk.CTkLabel(
            header, text="●", font=("Segoe UI", 12), text_color=COLORS["success"]
        )
        self.status_dot.pack(side="right", padx=(0, 4))

        self.status_label = ctk.CTkLabel(
            header, text="LIVE · 192.168.1.50:7777",
            font=font("xs", mono=True), text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="right")

        # Trait de séparation sous le header
        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep.grid(row=0, column=1, sticky="sew", padx=SPACING["lg"], pady=(56, 0))

    def set_connection_status(self, connected: bool, address: str = ""):
        """Met à jour la pastille de statut réseau du header."""
        self.status_dot.configure(text_color=COLORS["success"] if connected else COLORS["offline"])
        state = "LIVE" if connected else "HORS LIGNE"
        self.status_label.configure(text=f"{state}{' · ' + address if address else ''}")

    def register_panel(self, name: str, panel_widget):
        self.panels[name] = panel_widget

    def show_panel(self, name: str):
        if self.current_panel and self.current_panel in self.panels:
            self.panels[self.current_panel].pack_forget()

        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=COLORS["surface_raised"], text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["rail_icon"])

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