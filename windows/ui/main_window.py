"""
CLIPBOARD LAN - Main Window
Fenêtre principale avec sidebar et zone de contenu

CHEMIN: windows/ui/main_window.py
"""

import customtkinter as ctk
from typing import Optional, Callable

try:
    from .theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, ICONS
except ImportError:
    from theme import COLORS, FONTS, SPACING, RADIUS, DIMENSIONS, ICONS


class MainWindow(ctk.CTk):
    """
    Fenêtre principale de Clipboard LAN.
    
    Structure:
    - Sidebar gauche (navigation)
    - Zone de contenu principale (panels changeables)
    """
    
    def __init__(self, sync_manager=None):
        """
        Initialise la fenêtre principale.
        
        Args:
            sync_manager: Instance SyncManager (Phase 4)
        """
        super().__init__()
        
        self.sync_manager = sync_manager
        
        # Configuration fenêtre
        self.title("Clipboard LAN")
        self.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.configure(fg_color=COLORS["background"])
        
        ctk.set_appearance_mode("light")
        
        # Panels disponibles
        self.panels = {}
        self.current_panel = None
        self.nav_buttons = {}
        
        self._create_layout()
    
    def _create_layout(self):
        """Crée la structure générale (sidebar + contenu)."""
        # Container principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar()
        
        # Zone de contenu
        self.content_frame = ctk.CTkFrame(
            self, fg_color=COLORS["background"], corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=SPACING["lg"], pady=SPACING["lg"])
    
    def _create_sidebar(self):
        """Crée la barre latérale de navigation."""
        self.sidebar = ctk.CTkFrame(
            self, width=DIMENSIONS["sidebar_width"],
            fg_color=COLORS["sidebar"], corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Boutons de navigation
        nav_items = [
            ("dashboard", ICONS["dashboard"], "Tableau de bord"),
            ("devices", ICONS["devices"], "Appareils"),
            ("history", ICONS["history"], "Historique"),
            ("settings", ICONS["settings"], "Paramètres"),
        ]
        
        for i, (key, icon, tooltip) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=icon,
                font=ctk.CTkFont(size=20),
                width=50, height=50,
                corner_radius=RADIUS["md"],
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                command=lambda k=key: self.show_panel(k)
            )
            btn.grid(row=i, column=0, padx=15, pady=10)
            self.nav_buttons[key] = btn
    
    def register_panel(self, name: str, panel_widget):
        """
        Enregistre un panel dans la fenêtre.
        
        Args:
            name: Identifiant du panel
            panel_widget: Instance du widget panel
        """
        self.panels[name] = panel_widget
    
    def show_panel(self, name: str):
        """
        Affiche un panel spécifique.
        
        Args:
            name: Identifiant du panel à afficher
        """
        # Cacher le panel actuel
        if self.current_panel and self.current_panel in self.panels:
            self.panels[self.current_panel].pack_forget()
        
        # Mettre à jour l'état des boutons
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=COLORS["sidebar_active"])
            else:
                btn.configure(fg_color="transparent")
        
        # Afficher le nouveau panel
        if name in self.panels:
            self.panels[name].pack(fill="both", expand=True)
            self.current_panel = name
    
    def get_content_frame(self):
        """Retourne le frame de contenu pour y placer des panels."""
        return self.content_frame
    
    def update_status(self, status: dict):
        """
        Met à jour l'affichage avec un nouveau statut.
        
        Args:
            status: Dict de statut depuis SyncManager.get_status()
        """
        # Sera utilisé pour rafraîchir les panels affichés
        pass
    
    def run(self):
        """Lance la boucle principale de l'interface."""
        self.mainloop()


def create_main_window(sync_manager=None) -> MainWindow:
    """Factory pour créer la fenêtre principale."""
    return MainWindow(sync_manager=sync_manager)


if __name__ == "__main__":
    app = MainWindow()
    app.run()