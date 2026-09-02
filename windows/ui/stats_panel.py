"""
CLIPBOARD LAN - Stats Panel
Tableau de bord avec statistiques et cards

CHEMIN: windows/ui/stats_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, ICONS, get_font
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, ICONS, get_font


class StatCard(ctk.CTkFrame):
    """Card individuelle affichant une statistique."""
    
    def __init__(self, master, icon: str, title: str, value: str, 
                 subtitle: str = "", color: str = None):
        """
        Initialise une card de statistique.
        
        Args:
            master: Widget parent
            icon: Emoji/icône à afficher
            title: Titre de la stat
            value: Valeur principale (grand texte)
            subtitle: Texte secondaire optionnel
            color: Couleur d'accent optionnelle
        """
        super().__init__(
            master, fg_color=COLORS["card"], corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["card_border"]
        )
        
        color = color or COLORS["text_primary"]
        
        self.grid_columnconfigure(0, weight=1)
        
        # Icône
        icon_label = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=24),
            anchor="w"
        )
        icon_label.grid(row=0, column=0, sticky="w", padx=SPACING["md"], pady=(SPACING["md"], 0))
        
        # Titre
        title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_secondary"], anchor="w"
        )
        title_label.grid(row=1, column=0, sticky="w", padx=SPACING["md"], pady=(SPACING["xs"], 0))
        
        # Valeur
        value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_2xl"], weight="bold"),
            text_color=color, anchor="w"
        )
        value_label.grid(row=2, column=0, sticky="w", padx=SPACING["md"], pady=(SPACING["xs"], 0))
        
        # Sous-titre
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self, text=subtitle, font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
                text_color=COLORS["text_light"], anchor="w"
            )
            subtitle_label.grid(row=3, column=0, sticky="w", padx=SPACING["md"], pady=(0, SPACING["md"]))
        else:
            self.grid_rowconfigure(2, minsize=SPACING["md"])
    
    def update_value(self, value: str):
        """Met à jour la valeur affichée."""
        pass


class StatsPanel(ctk.CTkFrame):
    """
    Panel principal du tableau de bord.
    
    Affiche:
    - Cards de statistiques (appareils, syncs, etc.)
    - Statut de synchronisation en direct
    - Activité récente
    """
    
    def __init__(self, master, sync_manager=None):
        """
        Initialise le panel de statistiques.
        
        Args:
            master: Widget parent
            sync_manager: Instance SyncManager (Phase 4)
        """
        super().__init__(master, fg_color="transparent")
        
        self.sync_manager = sync_manager
        
        self._create_header()
        self._create_stats_grid()
        self._create_activity_section()
    
    def _create_header(self):
        """Crée l'en-tête du panel."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING["lg"]))
        
        title = ctk.CTkLabel(
            header, text="Tableau de bord",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_2xl"], weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        self.status_indicator = ctk.CTkLabel(
            header, text=f"{ICONS['connected']} Actif",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["success"]
        )
        self.status_indicator.pack(side="right")
    
    def _create_stats_grid(self):
        """Crée la grille de cards de statistiques."""
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", pady=(0, SPACING["lg"]))
        
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="stats")
        
        self.card_devices = StatCard(
            grid, ICONS["devices"], "Appareils connectés", "0",
            "0 de confiance", COLORS["accent_blue"]
        )
        self.card_devices.grid(row=0, column=0, padx=(0, SPACING["sm"]), sticky="nsew")
        
        self.card_syncs = StatCard(
            grid, ICONS["sync"], "Synchronisations", "0",
            "aujourd'hui", COLORS["accent_green"]
        )
        self.card_syncs.grid(row=0, column=1, padx=SPACING["sm"], sticky="nsew")
        
        self.card_success = StatCard(
            grid, ICONS["success"], "Taux de réussite", "100%",
            "sur 7 jours", COLORS["success"]
        )
        self.card_success.grid(row=0, column=2, padx=SPACING["sm"], sticky="nsew")
        
        self.card_data = StatCard(
            grid, ICONS["clipboard"], "Données transférées", "0 KB",
            "total", COLORS["accent_orange"]
        )
        self.card_data.grid(row=0, column=3, padx=(SPACING["sm"], 0), sticky="nsew")
    
    def _create_activity_section(self):
        """Crée la section d'activité récente."""
        section = ctk.CTkFrame(
            self, fg_color=COLORS["card"], corner_radius=RADIUS["lg"],
            border_width=1, border_color=COLORS["card_border"]
        )
        section.pack(fill="both", expand=True)
        
        title = ctk.CTkLabel(
            section, text="Activité récente",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_lg"], weight="bold"),
            text_color=COLORS["text_primary"], anchor="w"
        )
        title.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        self.activity_list = ctk.CTkScrollableFrame(
            section, fg_color="transparent"
        )
        self.activity_list.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Affiche un état vide quand pas d'activité."""
        empty_label = ctk.CTkLabel(
            self.activity_list, text="Aucune activité pour le moment",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_base"]),
            text_color=COLORS["text_light"]
        )
        empty_label.pack(pady=SPACING["2xl"])
    
    def add_activity_item(self, source: str, content_preview: str, timestamp: str):
        """
        Ajoute un item à la liste d'activité.
        
        Args:
            source: Appareil source (ex: "Android")
            content_preview: Aperçu du contenu synchronisé
            timestamp: Horodatage
        """
        item = ctk.CTkFrame(self.activity_list, fg_color=COLORS["background_light"], corner_radius=RADIUS["sm"])
        item.pack(fill="x", pady=SPACING["xs"])
        
        icon = ICONS["android"] if "android" in source.lower() else ICONS["windows"]
        
        text = ctk.CTkLabel(
            item, text=f"{icon} {source} → {content_preview}",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_primary"], anchor="w"
        )
        text.pack(side="left", padx=SPACING["sm"], pady=SPACING["sm"])
        
        time_label = ctk.CTkLabel(
            item, text=timestamp,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
            text_color=COLORS["text_light"]
        )
        time_label.pack(side="right", padx=SPACING["sm"])
    
    def refresh(self, status: dict):
        """
        Rafraîchit les statistiques affichées.
        
        Args:
            status: Dict de statut depuis SyncManager
        """
        connected = status.get("connected_devices", 0)
        # Mise à jour des cards (nécessite refonte pour update dynamique)


if __name__ == "__main__":
    print("✅ Stats Panel ready")