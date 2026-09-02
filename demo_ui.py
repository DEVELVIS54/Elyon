"""
CLIPBOARD LAN - Démo UI
Script pour visualiser l'interface sans backend complet

CHEMIN: demo_ui.py (à la racine du projet)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "windows", "ui"))

from main_window import MainWindow
from stats_panel import StatsPanel
from device_panel import DevicePanel
from history_panel import HistoryPanel


def main():
    app = MainWindow()
    
    content = app.get_content_frame()
    
    # Créer les panels
    stats = StatsPanel(content)
    devices = DevicePanel(content)
    history = HistoryPanel(content)
    
    # Enregistrer dans la fenêtre
    app.register_panel("dashboard", stats)
    app.register_panel("devices", devices)
    app.register_panel("history", history)
    app.register_panel("settings", stats)  # Placeholder
    
    # Données de démo pour voir le rendu
    devices.refresh_devices([
        {
            "device_id": "android-1",
            "device_name": "Samsung Galaxy S23",
            "is_connected": True,
            "is_trusted": True,
            "last_seen": "à l'instant"
        },
        {
            "device_id": "android-2",
            "device_name": "Pixel 8",
            "is_connected": False,
            "is_trusted": False,
            "last_seen": "il y a 2h"
        }
    ])
    
    stats.add_activity_item("Android", "Hello World...", "14:32")
    stats.add_activity_item("Windows", "Test synchronisation", "14:28")
    
    history.refresh_history([
        {
            "source_device_id": "Android",
            "content_type": "text/plain",
            "content_size": 1024,
            "status": "success",
            "sync_time": "14:32"
        },
        {
            "source_device_id": "Windows",
            "content_type": "text/plain",
            "content_size": 512,
            "status": "failed",
            "sync_time": "14:28"
        }
    ])
    
    # Afficher le dashboard par défaut
    app.show_panel("dashboard")
    
    app.run()


if __name__ == "__main__":
    main()