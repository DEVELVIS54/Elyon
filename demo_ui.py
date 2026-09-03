"""
CLIPBOARD LAN - Démo UI v2
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

    stats = StatsPanel(content)
    devices = DevicePanel(content)
    history = HistoryPanel(content)

    app.register_panel("dashboard", stats)
    app.register_panel("devices", devices)
    app.register_panel("history", history)
    app.register_panel("settings", stats)  # placeholder

    devices.refresh_devices([
        {"device_id": "android-a1f9", "device_name": "Galaxy S23", "is_connected": True,
         "is_trusted": True, "last_seen": "à l'instant"},
        {"device_id": "android-7c02", "device_name": "Pixel 8", "is_connected": False,
         "is_trusted": False, "last_seen": "il y a 2h"},
    ])

    stats.add_activity_item("android", "Hello World, ceci est un test…", "14:32", "128 B")
    stats.add_activity_item("windows", "https://github.com/DEVELVIS54", "14:28", "42 B")
    stats.update_readouts(devices=2, syncs=12, success_rate="100%", data_transferred="4.2 KB", uptime="02:14:09")

    history.refresh_history([
        {"source_device_id": "android", "content_type": "text/plain", "content_size": 1024,
         "status": "success", "sync_time": "14:32"},
        {"source_device_id": "windows", "content_type": "text/plain", "content_size": 512,
         "status": "failed", "sync_time": "14:28"},
    ])

    app.set_connection_status(True, "192.168.1.50:7777")
    app.show_panel("dashboard")
    app.run()


if __name__ == "__main__":
    main()