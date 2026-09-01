"""
CLIPBOARD LAN - Sync Manager
Orchestre la synchronisation complète entre Windows et Android

CHEMIN: windows/sync/sync_manager.py
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional


class SyncManager:
    """
    Orchestrateur principal de Clipboard LAN.
    
    Coordonne tous les modules:
    - Security (Phase 1)
    - Anti-Loop (Phase 1)
    - Clipboard (Phase 1)
    - WebSocket (Phase 2)
    - mDNS (Phase 2)
    - Protocol (Phase 2)
    - Database (Phase 3)
    """
    
    def __init__(self, device_id: str, device_name: str,
                 security_manager=None, clipboard_manager=None,
                 loop_detector=None, protocol_handler=None,
                 websocket_server=None, mdns_announcer=None,
                 db_manager=None, devices_manager=None,
                 history_manager=None, settings_manager=None):
        """
        Initialise le SyncManager avec tous les modules.
        
        Args:
            device_id: ID unique de cet appareil (Windows)
            device_name: Nom lisible de l'appareil
            *_manager: Instances des différents modules
        """
        self.device_id = device_id
        self.device_name = device_name
        
        # Modules Phase 1
        self.security = security_manager
        self.clipboard = clipboard_manager
        self.loop_detector = loop_detector
        
        # Modules Phase 2
        self.protocol = protocol_handler
        self.websocket = websocket_server
        self.mdns = mdns_announcer
        
        # Modules Phase 3
        self.db = db_manager
        self.devices = devices_manager
        self.history = history_manager
        self.settings = settings_manager
        
        self.is_running = False
        self.logger = logging.getLogger("SyncManager")
        self.logger.setLevel(logging.INFO)
        
        # Callbacks
        self._on_sync_callbacks = []
        self._on_device_connected_callbacks = []
        self._on_device_disconnected_callbacks = []
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure les handlers entre modules."""
        if self.websocket:
            self.websocket.on_message(self._handle_websocket_message)
            self.websocket.on_connect(self._handle_device_connect)
            self.websocket.on_disconnect(self._handle_device_disconnect)
        
        if self.clipboard:
            self.clipboard.on_change(self._handle_clipboard_change)
    
    def start(self):
        """Lance le SyncManager et tous les services."""
        self.logger.info(f"🚀 Démarrage SyncManager: {self.device_name}")
        
        try:
            # Lancer mDNS
            if self.mdns:
                self.mdns.start()
                self.logger.info("✅ mDNS Announcer démarré")
            
            # Lancer clipboard monitoring
            if self.clipboard:
                self.clipboard.start_monitoring()
                self.logger.info("✅ Clipboard monitoring démarré")
            
            self.is_running = True
            self.logger.info("✅ SyncManager complètement démarré")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage: {e}")
            raise
    
    def stop(self):
        """Arrête le SyncManager."""
        self.logger.info("🛑 Arrêt SyncManager")
        
        try:
            if self.mdns:
                self.mdns.stop()
            
            if self.clipboard:
                self.clipboard.stop_monitoring()
            
            self.is_running = False
            self.logger.info("✅ SyncManager arrêté")
        
        except Exception as e:
            self.logger.error(f"Erreur arrêt: {e}")
    
    def _handle_websocket_message(self, device_id: str, message: dict):
        """Traite un message WebSocket reçu."""
        try:
            # 1. Valider le message
            if self.protocol:
                valid, reason = self.protocol.validate_message(message)
                if not valid:
                    self.logger.warning(f"Message invalide de {device_id}: {reason}")
                    return
            
            message_type = message.get("type")
            
            if message_type == "SYNC":
                self._handle_sync_message(device_id, message)
            elif message_type == "PING":
                self._handle_ping(device_id)
        
        except Exception as e:
            self.logger.error(f"Erreur traitement message: {e}")
    
    def _handle_sync_message(self, device_id: str, message: dict):
        """Traite un message SYNC (synchronisation clipboard)."""
        content = message.get("content", "")
        content_type = message.get("content_type", "text/plain")
        
        # 1. Vérifier anti-boucle
        if self.loop_detector:
            should_sync, reason = self.loop_detector.should_sync(content, device_id)
            if not should_sync:
                self.logger.info(f"Sync ignorée: {reason}")
                return
        
        # 2. Écrire dans le clipboard
        if self.clipboard:
            success = self.clipboard.write(content)
            if not success:
                self.logger.error("Échec écriture clipboard")
                return
        
        # 3. Marquer comme reçu (anti-loop)
        if self.loop_detector:
            self.loop_detector.mark_received(content, device_id)
        
        # 4. Sauvegarder dans l'historique
        if self.history and self.security:
            content_hash = self.security.sha256(content)
            self.history.add_sync(
                device_id, content_hash, 
                len(content), content_type, "success"
            )
        
        # 5. Mettre à jour last_seen
        if self.devices:
            self.devices.update_last_seen(device_id)
        
        self.logger.info(f"✅ Sync reçu de {device_id}: {len(content)} caractères")
        
        # Notifier les callbacks
        for callback in self._on_sync_callbacks:
            try:
                callback(device_id, content)
            except Exception as e:
                self.logger.error(f"Erreur callback sync: {e}")
    
    def _handle_clipboard_change(self, content: str):
        """Traite un changement local du clipboard."""
        if not content:
            return
        
        # Vérifier anti-boucle
        if self.loop_detector:
            should_sync, reason = self.loop_detector.should_sync(
                content, self.device_id
            )
            if not should_sync:
                return
            
            self.loop_detector.mark_sent(content)
        
        # Créer le message SYNC
        if self.protocol:
            message = self.protocol.create_sync(self.device_id, content)
            
            # Broadcaster à tous les appareils connectés
            if self.websocket:
                asyncio.create_task(self.websocket.broadcast(message))
        
        self.logger.info(f"📤 Clipboard local changé: {len(content)} caractères")
    
    def _handle_device_connect(self, device_id: str, device_name: str):
        """Traite la connexion d'un nouvel appareil."""
        self.logger.info(f"📱 Appareil connecté: {device_name} ({device_id})")
        
        if self.devices:
            device = self.devices.get_device(device_id)
            if not device:
                # Nouvel appareil
                self.devices.add_device(device_id, device_name, "")
            
            self.devices.update_last_seen(device_id)
        
        for callback in self._on_device_connected_callbacks:
            try:
                callback(device_id, device_name)
            except Exception as e:
                self.logger.error(f"Erreur callback connect: {e}")
    
    def _handle_device_disconnect(self, device_id: str):
        """Traite la déconnexion d'un appareil."""
        self.logger.info(f"📴 Appareil déconnecté: {device_id}")
        
        for callback in self._on_device_disconnected_callbacks:
            try:
                callback(device_id)
            except Exception as e:
                self.logger.error(f"Erreur callback disconnect: {e}")
    
    def _handle_ping(self, device_id: str):
        """Répond à un PING."""
        if self.protocol and self.websocket:
            pong = self.protocol.create_pong()
            asyncio.create_task(
                self.websocket.send_to_device(device_id, pong)
            )
    
    def on_sync(self, callback):
        """Enregistre un callback pour les syncs."""
        self._on_sync_callbacks.append(callback)
    
    def on_device_connected(self, callback):
        """Enregistre un callback pour les connexions."""
        self._on_device_connected_callbacks.append(callback)
    
    def on_device_disconnected(self, callback):
        """Enregistre un callback pour les déconnexions."""
        self._on_device_disconnected_callbacks.append(callback)
    
    def get_status(self) -> dict:
        """Retourne le statut complet du système."""
        status = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "is_running": self.is_running,
            "timestamp": datetime.now().isoformat(),
        }
        
        if self.websocket:
            status["websocket"] = self.websocket.get_info()
        
        if self.clipboard:
            status["clipboard"] = self.clipboard.get_info()
        
        if self.devices:
            status["connected_devices"] = len(self.devices.get_all_devices())
        
        return status


if __name__ == "__main__":
    print("✅ Sync Manager ready")