"""
CLIPBOARD LAN - History Panel
Journal des synchronisations — thème clair.

CHEMIN: windows/ui/history_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, font


class HistoryRow(ctk.CTkFrame):
    def __init__(self, master, source_device: str, content_type: str,
                 content_size: int, status: str, sync_time: str):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(3, weight=1)

        status_color = COLORS["success"] if status == "success" else COLORS["error"]
        mark = ctk.CTkLabel(self, text="✓" if status == "success" else "✕",
                            font=font("sm", "bold"), text_color=status_color, width=20)
        mark.grid(row=0, column=0, sticky="w")

        time_lbl = ctk.CTkLabel(self, text=sync_time, font=font("xs"), text_color=COLORS["text_light"],
                                width=50, anchor="w")
        time_lbl.grid(row=0, column=1, sticky="w", padx=(SPACING["sm"], SPACING["md"]))

        badge = ctk.CTkFrame(self, fg_color=COLORS["accent_soft"], corner_radius=RADIUS["sm"])
        badge.grid(row=0, column=2, sticky="w", padx=(0, SPACING["md"]))
        source_lbl = ctk.CTkLabel(badge, text=source_device.capitalize(), font=font("xs", "bold"),
                                  text_color=COLORS["accent"])
        source_lbl.pack(padx=8, pady=2)

        type_lbl = ctk.CTkLabel(self, text=content_type, font=font("sm"),
                                text_color=COLORS["text_primary"], anchor="w")
        type_lbl.grid(row=0, column=3, sticky="w")

        size_lbl = ctk.CTkLabel(self, text=self._format_size(content_size), font=font("xs"),
                                text_color=COLORS["text_light"], anchor="e")
        size_lbl.grid(row=0, column=4, sticky="e")

        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(SPACING["sm"], 0))

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"


class HistoryPanel(ctk.CTkFrame):
    def __init__(self, master, history_manager=None):
        super().__init__(master, fg_color="transparent")
        self.history_manager = history_manager

        self._create_header()
        self._create_list_container()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(SPACING["md"], SPACING["md"]))

        title = ctk.CTkLabel(header, text="Historique", font=font("xl", "bold"),
                             text_color=COLORS["text_primary"])
        title.pack(side="left")

        self.filter_var = ctk.StringVar(value="Tous")
        filter_menu = ctk.CTkOptionMenu(
            header, values=["Tous", "Réussis", "Échoués"],
            variable=self.filter_var, width=130, height=30,
            fg_color=COLORS["card"], button_color=COLORS["accent_soft"],
            button_hover_color=COLORS["card_hover"],
            text_color=COLORS["text_secondary"], font=font("sm"),
            dropdown_fg_color=COLORS["card"],
            command=self._apply_filter
        )
        filter_menu.pack(side="right", padx=(SPACING["sm"], 0))

        clear_btn = ctk.CTkButton(
            header, text="Effacer", width=76, height=30,
            fg_color="transparent", hover_color=COLORS["card_hover"],
            text_color=COLORS["text_secondary"], border_width=1, border_color=COLORS["border"],
            font=font("sm"), corner_radius=RADIUS["md"],
            command=self._clear_history
        )
        clear_btn.pack(side="right")

    def _create_list_container(self):
        container = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=RADIUS["xl"],
                                 border_width=1, border_color=COLORS["card_border"])
        container.pack(fill="both", expand=True)

        self.history_list_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.history_list_frame.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        self._show_empty_state()

    def _show_empty_state(self):
        empty_label = ctk.CTkLabel(self.history_list_frame, text="Aucun historique pour le moment.",
                                   font=font("sm"), text_color=COLORS["text_light"])
        empty_label.pack(pady=SPACING["2xl"])

    def refresh_history(self, history_entries: list):
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        if not history_entries:
            self._show_empty_state()
            return

        for entry in history_entries:
            row = HistoryRow(
                self.history_list_frame,
                source_device=entry.get("source_device_id", "inconnu"),
                content_type=entry.get("content_type", "text/plain"),
                content_size=entry.get("content_size", 0),
                status=entry.get("status", "success"),
                sync_time=entry.get("sync_time", "")
            )
            row.pack(fill="x", pady=(0, SPACING["xs"]))

    def _apply_filter(self, choice: str):
        pass

    def _clear_history(self):
        if self.history_manager:
            self.history_manager.clear_old_history(days=0)
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        self._show_empty_state()


if __name__ == "__main__":
    print("✅ History Panel v3 ready — light theme")