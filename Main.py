"""
CLIPBOARD LAN - Point d'entrée principal
Assemble Phases 1-5 en une application complète

CHEMIN: main.py (à la racine du projet)
"""

import sys
import os
import threading
import asyncio
import uuid
import logging
import socket
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "windows", "ui"))

from config import DB_PATH, KEYS_DIR, WEBSOCKET_PORT

# Phase 1
from windows_security import SecurityManager
from windows_clipboard import ClipboardManager
from windows_anti_loop import LoopDetector

# Phase 2
from windows.network.protocol import ProtocolHandler
from windows.network.websocket_server import WebSocketServer
from windows.network.mdns_announcer import MDNSAnnouncer

# Phase 3
from windows.storage.database import DatabaseManager
from windows.storage.devices import DevicesManager
from windows.storage.history import HistoryManager
from windows.storage.settings import SettingsManager

# Phase 4
from windows.sync.sync_manager import SyncManager
from windows.sync.device_manager import DeviceManager
from windows.sync.connection_handler import ConnectionHandler

# Phase 5
from main_window import MainWindow
from stats_panel import StatsPanel
from device_panel import DevicePanel
from history_panel import HistoryPanel
from system_tray import SystemTray


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("Main")


def get_or_create_device_id(settings: SettingsManager) -> str:
    """Récupère l'ID de cet appareil Windows, ou en crée un persistant."""
    device_id = settings.get("device_id")
    if not device_id:
        device_id = f"windows-{uuid.uuid4().hex[:12]}"
        settings.set("device_id", device_id)
    return device_id


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class ClipboardLANApp:
    """Assemble toutes les phases et démarre l'application."""

    def __init__(self):
        self.start_time = datetime.now()
        self._sync_count_today = 0

        self._init_storage()
        self._init_core()
        self._init_network()
        self._init_sync()
        self._init_ui()
        self._wire_events()

    # ------------------------------------------------------------------
    # Initialisation par phase
    # ------------------------------------------------------------------

    def _init_storage(self):
        """Phase 3."""
        self.db = DatabaseManager(Path(DB_PATH))
        self.db.migrate()

        self.devices_storage = DevicesManager(self.db)
        self.history = HistoryManager(self.db)
        self.settings = SettingsManager(self.db)

        self.device_id = get_or_create_device_id(self.settings)
        self.device_name = socket.gethostname()

    def _init_core(self):
        """Phase 1."""
        self.security = SecurityManager(Path(KEYS_DIR))
        self.clipboard = ClipboardManager(
            max_size=self.settings.get("max_clipboard_size")
        )
        self.loop_detector = LoopDetector()
        self.loop_detector.set_device_id(self.device_id)

    def _init_network(self):
        """Phase 2."""
        self.protocol = ProtocolHandler(security_manager=self.security)
        self.websocket = WebSocketServer(host="0.0.0.0", port=WEBSOCKET_PORT)
        self.mdns = MDNSAnnouncer(
            device_id=self.device_id,
            device_name=self.device_name,
            port=WEBSOCKET_PORT,
        )

    def _init_sync(self):
        """Phase 4."""
        self.device_manager = DeviceManager(devices_storage=self.devices_storage)
        self.connection_handler = ConnectionHandler()

        self.sync_manager = SyncManager(
            device_id=self.device_id,
            device_name=self.device_name,
            security_manager=self.security,
            clipboard_manager=self.clipboard,
            loop_detector=self.loop_detector,
            protocol_handler=self.protocol,
            websocket_server=self.websocket,
            mdns_announcer=self.mdns,
            db_manager=self.db,
            devices_manager=self.devices_storage,
            history_manager=self.history,
            settings_manager=self.settings,
        )

    def _init_ui(self):
        """Phase 5."""
        self.window = MainWindow(sync_manager=self.sync_manager)
        content = self.window.get_content_frame()

        self.stats_panel = StatsPanel(content, sync_manager=self.sync_manager)
        self.device_panel = DevicePanel(content, device_manager=self.device_manager)
        self.history_panel = HistoryPanel(content, history_manager=self.history)

        self.window.register_panel("dashboard", self.stats_panel)
        self.window.register_panel("devices", self.device_panel)
        self.window.register_panel("history", self.history_panel)
        self.window.register_panel("settings", self.stats_panel)  # placeholder
        self.window.show_panel("dashboard")

        self.device_panel.on_approve_device(self._on_approve_device)
        self.device_panel.on_remove_device(self._on_remove_device)

        self.tray = SystemTray(
            app_name="Clipboard LAN",
            on_show=self._show_window,
            on_quit=self._quit_app,
        )

        # Fermer la fenêtre = minimiser dans la barre système
        self.window.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    # ------------------------------------------------------------------
    # Câblage des évènements backend -> UI
    # ------------------------------------------------------------------

    def _wire_events(self):
        self.sync_manager.on_sync(self._on_sync_received)
        self.sync_manager.on_device_connected(self._on_device_connected)
        self.sync_manager.on_device_disconnected(self._on_device_disconnected)

    def _on_sync_received(self, device_id: str, content: str):
        self._sync_count_today += 1
        preview = content[:60] + ("…" if len(content) > 60 else "")
        source = "android" if "android" in device_id.lower() else device_id

        self.window.after(0, lambda: self.stats_panel.add_activity_item(
            source, preview, datetime.now().strftime("%H:%M"), f"{len(content)} B"
        ))
        self.window.after(0, self._refresh_readouts)
        self.window.after(0, self._refresh_history)

    def _on_device_connected(self, device_id: str, device_name: str):
        info = self.device_manager.handle_device_connect(device_id, device_name)
        self.window.after(0, self._refresh_devices)

        if info.get("is_new"):
            self.tray.show_notification(
                "Nouvel appareil", f"{device_name} demande à se connecter"
            )

    def _on_device_disconnected(self, device_id: str):
        self.device_manager.handle_device_disconnect(device_id)
        self.window.after(0, self._refresh_devices)

    def _on_approve_device(self, device_id: str):
        self.device_manager.approve_device(device_id)
        self._refresh_devices()

    def _on_remove_device(self, device_id: str):
        self.device_manager.reject_device(device_id)
        self._refresh_devices()

    # ------------------------------------------------------------------
    # Rafraîchissements UI
    # ------------------------------------------------------------------

    def _refresh_devices(self):
        self.device_panel.refresh_devices(self.device_manager.get_connected_devices())

    def _refresh_history(self):
        self.history_panel.refresh_history(self.history.get_history(limit=50))

    def _refresh_readouts(self):
        stats = self.history.get_stats()
        elapsed = datetime.now() - self.start_time
        uptime = str(elapsed).split(".")[0].rjust(8, "0")

        total = stats.get("total_syncs", 0) or 0
        success = stats.get("success_syncs", 0) or 0
        rate = f"{int(success / total * 100)}%" if total else "—"

        self.stats_panel.update_readouts(
            devices=len(self.device_manager.get_connected_devices()),
            syncs=self._sync_count_today,
            success_rate=rate,
            data_transferred=f"{stats.get('total_size', 0) / 1024:.1f} KB",
            uptime=uptime,
        )

    def _tick(self):
        """Boucle légère pour rafraîchir l'uptime toutes les secondes."""
        self._refresh_readouts()
        self.window.after(1000, self._tick)

    # ------------------------------------------------------------------
    # Fenêtre / tray
    # ------------------------------------------------------------------

    def _minimize_to_tray(self):
        self.window.withdraw()

    def _show_window(self):
        self.window.after(0, self.window.deiconify)

    def _quit_app(self):
        logger.info("🛑 Fermeture de l'application")
        self.sync_manager.stop()
        self.window.after(0, self.window.destroy)

    # ------------------------------------------------------------------
    # Démarrage
    # ------------------------------------------------------------------

    def _start_backend_loop(self):
        """Lance le serveur WebSocket (asyncio) dans un thread séparé."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.websocket.start())
        except Exception as e:
            logger.error(f"Erreur boucle réseau: {e}")

    def run(self):
        ip = get_local_ip()
        logger.info(f"🚀 Clipboard LAN — {self.device_name} ({self.device_id})")
        logger.info(f"📡 Écoute sur {ip}:{WEBSOCKET_PORT}")

        self.sync_manager.start()
        self.window.set_connection_status(True, f"{ip}:{WEBSOCKET_PORT}")

        # Serveur WebSocket dans un thread (asyncio ne peut pas partager
        # la boucle Tkinter)
        backend_thread = threading.Thread(target=self._start_backend_loop, daemon=True)
        backend_thread.start()

        # Icône barre système dans un thread
        self.tray.start_in_thread()

        # Rafraîchissement initial + boucle d'uptime
        self._refresh_devices()
        self._refresh_history()
        self.window.after(1000, self._tick)

        self.window.run()


if __name__ == "__main__":
    app = ClipboardLANApp()
    app.run()