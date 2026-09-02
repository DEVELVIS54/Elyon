"""
CLIPBOARD LAN - Device Panel
Affiche la liste des appareils connectés/connus

CHEMIN: windows/ui/device_panel.py
"""

import customtkinter as ctk

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, ICONS, get_status_color
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, ICONS, get_status_color


class DeviceCard(ctk.CTkFrame):
    """Card représentant un appareil."""
    
    def __init__(self, master, device_id: str, device_name: str,
                 is_connected: bool = False, is_trusted: bool = False,
                 last_seen: str = "", on_approve=None, on_remove=None):
        """
        Initialise une card d'appareil.
        
        Args:
            master: Widget parent
            device_id: ID de l'appareil
            device_name: Nom de l'appareil
            is_connected: Statut de connexion
            is_trusted: Statut de confiance
            last_seen: Dernière activité
            on_approve: Callback pour approuver
            on_remove: Callback pour supprimer
        """
        super().__init__(
            master, fg_color=COLORS["card"], corner_radius=RADIUS["md"],
            border_width=1, border_color=COLORS["card_border"]
        )
        
        self.device_id = device_id
        
        self.grid_columnconfigure(1, weight=1)
        
        # Icône statut
        status_icon = ICONS["connected"] if is_connected else ICONS["disconnected"]
        icon_label = ctk.CTkLabel(
            self, text=status_icon, font=ctk.CTkFont(size=16)
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=SPACING["md"], pady=SPACING["md"])
        
        # Nom et infos
        name_label = ctk.CTkLabel(
            self, text=device_name,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_base"], weight="bold"),
            text_color=COLORS["text_primary"], anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", pady=(SPACING["sm"], 0))
        
        trust_text = "Approuvé" if is_trusted else "En attente d'approbation"
        trust_color = COLORS["success"] if is_trusted else COLORS["warning"]
        
        info_label = ctk.CTkLabel(
            self, text=f"{trust_text} • {last_seen}",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
            text_color=trust_color, anchor="w"
        )
        info_label.grid(row=1, column=1, sticky="w", pady=(0, SPACING["sm"]))
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=SPACING["md"])
        
        if not is_trusted and on_approve:
            approve_btn = ctk.CTkButton(
                actions_frame, text="Approuver", width=90, height=28,
                fg_color=COLORS["success"], hover_color="#1CA34E",
                font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xs"]),
                corner_radius=RADIUS["sm"],
                command=lambda: on_approve(device_id)
            )
            approve_btn.pack(side="left", padx=(0, SPACING["xs"]))
        
        if on_remove:
            remove_btn = ctk.CTkButton(
                actions_frame, text="✕", width=28, height=28,
                fg_color="transparent", hover_color=COLORS["error"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
                corner_radius=RADIUS["sm"],
                command=lambda: on_remove(device_id)
            )
            remove_btn.pack(side="left")


class DevicePanel(ctk.CTkFrame):
    """
    Panel affichant la liste des appareils.
    """
    
    def __init__(self, master, device_manager=None):
        """
        Initialise le panel des appareils.
        
        Args:
            master: Widget parent
            device_manager: Instance DeviceManager (Phase 4)
        """
        super().__init__(master, fg_color="transparent")
        
        self.device_manager = device_manager
        self._on_approve_callback = None
        self._on_remove_callback = None
        
        self._create_header()
        self._create_device_list()
    
    def _create_header(self):
        """Crée l'en-tête du panel."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING["lg"]))
        
        title = ctk.CTkLabel(
            header, text="Appareils",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_2xl"], weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
    
    def _create_device_list(self):
        """Crée la liste scrollable des appareils."""
        self.device_list_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.device_list_frame.pack(fill="both", expand=True)
        
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Affiche un état vide."""
        empty_label = ctk.CTkLabel(
            self.device_list_frame, 
            text=f"{ICONS['devices']} Aucun appareil connecté\n\nLancez l'app Android pour vous connecter",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_base"]),
            text_color=COLORS["text_light"], justify="center"
        )
        empty_label.pack(pady=SPACING["2xl"])
    
    def refresh_devices(self, devices: list):
        """
        Rafraîchit la liste des appareils affichés.
        
        Args:
            devices: Liste de dicts avec info appareils
        """
        # Nettoyer la liste actuelle
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()
        
        if not devices:
            self._show_empty_state()
            return
        
        for device in devices:
            card = DeviceCard(
                self.device_list_frame,
                device_id=device.get("device_id", ""),
                device_name=device.get("device_name", "Appareil inconnu"),
                is_connected=device.get("is_connected", True),
                is_trusted=device.get("is_trusted", False),
                last_seen=device.get("last_seen", "à l'instant"),
                on_approve=self._on_approve_callback,
                on_remove=self._on_remove_callback
            )
            card.pack(fill="x", pady=SPACING["xs"])
    
    def on_approve_device(self, callback):
        """Enregistre le callback d'approbation."""
        self._on_approve_callback = callback
    
    def on_remove_device(self, callback):
        """Enregistre le callback de suppression."""
        self._on_remove_callback = callback


if __name__ == "__main__":
    print("✅ Device Panel ready")