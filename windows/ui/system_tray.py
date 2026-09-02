"""
CLIPBOARD LAN - System Tray
Gère l'icône dans la barre système Windows

CHEMIN: windows/ui/system_tray.py
"""

import logging
import threading
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    raise ImportError(
        "pystray/Pillow not installed. Run: pip install pystray==0.19.5 Pillow==10.2.0"
    )


class SystemTray:
    """
    Gère l'icône et le menu dans la barre système Windows.
    
    Permet à l'application de tourner discrètement en arrière-plan.
    """
    
    def __init__(self, app_name: str = "Clipboard LAN",
                 on_show: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None):
        """
        Initialise l'icône système.
        
        Args:
            app_name: Nom affiché dans le menu
            on_show: Callback pour afficher la fenêtre principale
            on_quit: Callback pour quitter l'application
        """
        self.app_name = app_name
        self.on_show = on_show
        self.on_quit = on_quit
        
        self.icon: Optional[pystray.Icon] = None
        self.is_running = False
        
        self.logger = logging.getLogger("SystemTray")
        self.logger.setLevel(logging.INFO)
        
        self._status_text = "Actif"
    
    def _create_icon_image(self, connected: bool = True) -> Image.Image:
        """
        Crée l'image de l'icône (simple cercle coloré).
        
        Args:
            connected: Si True, icône verte, sinon grise
        
        Returns:
            Image PIL pour l'icône
        """
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Couleur selon statut
        color = (34, 197, 94, 255) if connected else (139, 149, 165, 255)
        
        # Cercle de fond
        draw.ellipse([4, 4, size - 4, size - 4], fill=(26, 35, 50, 255))
        
        # Point de statut
        draw.ellipse([size - 24, size - 24, size - 4, size - 4], fill=color)
        
        # "C" pour Clipboard au centre
        draw.text((size // 2 - 8, size // 2 - 12), "C", fill=(255, 255, 255, 255))
        
        return image
    
    def _build_menu(self) -> "pystray.Menu":
        """Construit le menu contextuel."""
        return pystray.Menu(
            pystray.MenuItem(
                self.app_name, None, enabled=False
            ),
            pystray.MenuItem(
                lambda item: f"Statut: {self._status_text}", None, enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Afficher", self._handle_show, default=True
            ),
            pystray.MenuItem(
                "Quitter", self._handle_quit
            ),
        )
    
    def _handle_show(self, icon=None, item=None):
        """Gère le clic sur 'Afficher'."""
        if self.on_show:
            try:
                self.on_show()
            except Exception as e:
                self.logger.error(f"Erreur on_show: {e}")
    
    def _handle_quit(self, icon=None, item=None):
        """Gère le clic sur 'Quitter'."""
        self.stop()
        
        if self.on_quit:
            try:
                self.on_quit()
            except Exception as e:
                self.logger.error(f"Erreur on_quit: {e}")
    
    def update_status(self, connected: bool, status_text: str = None):
        """
        Met à jour l'icône selon le statut de connexion.
        
        Args:
            connected: État de connexion
            status_text: Texte de statut optionnel
        """
        self._status_text = status_text or ("Connecté" if connected else "Déconnecté")
        
        if self.icon:
            self.icon.icon = self._create_icon_image(connected)
            self.icon.menu = self._build_menu()
    
    def start(self):
        """Lance l'icône système (bloquant, à utiliser dans un thread)."""
        self.icon = pystray.Icon(
            "clipboard_lan",
            icon=self._create_icon_image(True),
            title=self.app_name,
            menu=self._build_menu()
        )
        
        self.is_running = True
        self.logger.info("✅ System Tray démarré")
        self.icon.run()
    
    def start_in_thread(self):
        """Lance l'icône système dans un thread séparé (non-bloquant)."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Arrête l'icône système."""
        if self.icon:
            self.icon.stop()
        
        self.is_running = False
        self.logger.info("✅ System Tray arrêté")
    
    def show_notification(self, title: str, message: str):
        """
        Affiche une notification système.
        
        Args:
            title: Titre de la notification
            message: Message de la notification
        """
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                self.logger.error(f"Erreur notification: {e}")


if __name__ == "__main__":
    print("✅ System Tray ready")