"""
CLIPBOARD LAN - History Panel
Affiche l'historique des synchronisations

CHEMIN: windows/ui/history_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, ICONS
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, ICONS


class HistoryItem(ctk.CTkFrame):
    """Ligne représentant une entrée d'historique."""
    
    def __init__(self, master, source_device: str, content_type: str,
                 content_size: int, status: str, sync_time: str):
        """
        Initialise une entrée d'historique.
        
        Args:
            master: Widget parent
            source_device: Appareil source
            content_type: Type de contenu
            content_size: Taille en octets
            status: success/failed
            sync_time: Horodatage
        """
        super().__init__(
            master, fg_color=COLORS["card"], corner_radius=RADIUS["sm"],
            border_width=1, border_color=COLORS["card_border"]
        )
        
        status_icon = ICONS["success"] if status == "success" else ICONS["error"]
        status_color = COLORS["success"] if status == "success" else COLORS["error"]
        
        device_icon = ICONS["android"] if "android" in source_device.lower() else ICONS["windows"]
        
        self.grid_columnconfigure(1, weight=1)
        
        icon_label = ctk.CTkLabel(self, text=status_icon, font=ctk.CTkFont(size=16))
        icon_label.grid(row=0, column=0, padx=SPACING["md"], pady=SPACING["sm"])
        
        info_text = f"{device_icon} {source_device} • {content_type}"
        info_label = ctk.CTkLabel(
            self, text=info_text,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_primary"], anchor="w"
        )
        info_label.grid(row=0, column=1, sticky="w", pady=SPACING["sm"])
        
        size_text = self._format_size(content_size)
        size_label = ctk.CTkLabel(
            self, text=size_text,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
            text_color=COLORS["text_secondary"]
        )
        size_label.grid(row=0, column=2, padx=SPACING["md"])
        
        time_label = ctk.CTkLabel(
            self, text=sync_time,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
            text_color=COLORS["text_light"]
        )
        time_label.grid(row=0, column=3, padx=SPACING["md"])
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Formate une taille en octets de façon lisible."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


class HistoryPanel(ctk.CTkFrame):
    """
    Panel affichant l'historique complet des synchronisations.
    """
    
    def __init__(self, master, history_manager=None):
        """
        Initialise le panel d'historique.
        
        Args:
            master: Widget parent
            history_manager: Instance HistoryManager (Phase 3)
        """
        super().__init__(master, fg_color="transparent")
        
        self.history_manager = history_manager
        
        self._create_header()
        self._create_filter_bar()
        self._create_history_list()
    
    def _create_header(self):
        """Crée l'en-tête du panel."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING["md"]))
        
        title = ctk.CTkLabel(
            header, text="Historique",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_2xl"], weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            header, text="Effacer tout", width=100, height=32,
            fg_color="transparent", hover_color=COLORS["card_hover"],
            text_color=COLORS["text_secondary"], border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
            corner_radius=RADIUS["sm"],
            command=self._clear_history
        )
        clear_btn.pack(side="right")
    
    def _create_filter_bar(self):
        """Crée la barre de filtres."""
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.pack(fill="x", pady=(0, SPACING["md"]))
        
        self.filter_var = ctk.StringVar(value="Tous")
        filter_menu = ctk.CTkOptionMenu(
            filter_bar, values=["Tous", "Réussis", "Échoués"],
            variable=self.filter_var, width=140, height=32,
            fg_color=COLORS["card"], button_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            command=self._apply_filter
        )
        filter_menu.pack(side="left")
    
    def _create_history_list(self):
        """Crée la liste scrollable de l'historique."""
        self.history_list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.history_list_frame.pack(fill="both", expand=True)
        
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Affiche un état vide."""
        empty_label = ctk.CTkLabel(
            self.history_list_frame,
            text=f"{ICONS['history']} Aucun historique pour le moment",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_base"]),
            text_color=COLORS["text_light"]
        )
        empty_label.pack(pady=SPACING["2xl"])
    
    def refresh_history(self, history_entries: list):
        """
        Rafraîchit la liste d'historique affichée.
        
        Args:
            history_entries: Liste de dicts avec entrées d'historique
        """
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        
        if not history_entries:
            self._show_empty_state()
            return
        
        for entry in history_entries:
            item = HistoryItem(
                self.history_list_frame,
                source_device=entry.get("source_device_id", "Inconnu"),
                content_type=entry.get("content_type", "text/plain"),
                content_size=entry.get("content_size", 0),
                status=entry.get("status", "success"),
                sync_time=entry.get("sync_time", "")
            )
            item.pack(fill="x", pady=SPACING["xs"])
    
    def _apply_filter(self, choice: str):
        """Applique le filtre sélectionné."""
        # À connecter avec le history_manager pour filtrer les résultats
        pass
    
    def _clear_history(self):
        """Efface tout l'historique."""
        if self.history_manager:
            self.history_manager.clear_old_history(days=0)
        
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        self._show_empty_state()


if __name__ == "__main__":
    print("✅ History Panel ready")