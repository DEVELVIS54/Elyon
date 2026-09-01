"""
CLIPBOARD LAN - Device Manager
Gère les appareils connectés et leur cycle de vie

CHEMIN: windows/sync/device_manager.py
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime


class DeviceManager:
    """
    Gère les appareils connectés au système.
    
    Responsabilités:
    - Suivre les appareils actifs
    - Gérer l'authentification
    - Gérer les permissions
    - Coordonner avec la base de données
    """
    
    def __init__(self, devices_storage=None):
        """
        Initialise le DeviceManager.
        
        Args:
            devices_storage: Instance DevicesManager (Phase 3)
        """
        self.storage = devices_storage
        self.connected_devices: Dict[str, dict] = {}
        
        self.logger = logging.getLogger("DeviceManager")
        self.logger.setLevel(logging.INFO)
        
        self._on_new_device_callbacks = []
        self._on_device_approved_callbacks = []
    
    def handle_device_connect(self, device_id: str, device_name: str, 
                              public_key: str = "") -> dict:
        """
        Gère la connexion d'un appareil.
        
        Args:
            device_id: ID unique de l'appareil
            device_name: Nom de l'appareil
            public_key: Clé publique RSA
        
        Returns:
            Info de l'appareil avec statut
        """
        is_new = False
        is_trusted = False
        
        if self.storage:
            existing = self.storage.get_device(device_id)
            
            if existing:
                # Appareil connu
                is_trusted = bool(existing.get("is_trusted", False))
                self.storage.update_last_seen(device_id)
                self.logger.info(f"✅ Appareil connu reconnecté: {device_name}")
            else:
                # Nouvel appareil
                is_new = True
                self.storage.add_device(device_id, device_name, public_key)
                self.logger.info(f"🆕 Nouvel appareil détecté: {device_name}")
        else:
            # Pas de storage configuré = toujours considéré comme nouveau
            is_new = True
            self.logger.info(f"🆕 Nouvel appareil détecté (pas de storage): {device_name}")
        
        # Déclencher le callback si c'est un nouvel appareil
        if is_new:
            for callback in self._on_new_device_callbacks:
                try:
                    callback(device_id, device_name)
                except Exception as e:
                    self.logger.error(f"Erreur callback new device: {e}")
        
        # Ajouter aux connectés
        device_info = {
            "device_id": device_id,
            "device_name": device_name,
            "is_trusted": is_trusted,
            "is_new": is_new,
            "connected_at": datetime.now().isoformat(),
        }
        
        self.connected_devices[device_id] = device_info
        
        return device_info
    
    def handle_device_disconnect(self, device_id: str):
        """
        Gère la déconnexion d'un appareil.
        
        Args:
            device_id: ID de l'appareil déconnecté
        """
        if device_id in self.connected_devices:
            device_name = self.connected_devices[device_id].get("device_name", "Unknown")
            del self.connected_devices[device_id]
            self.logger.info(f"📴 Appareil déconnecté: {device_name}")
    
    def approve_device(self, device_id: str) -> bool:
        """
        Approuve un appareil (le marque comme trusted).
        
        Args:
            device_id: ID de l'appareil à approuver
        
        Returns:
            True si succès
        """
        if self.storage:
            success = self.storage.trust_device(device_id)
            
            if success and device_id in self.connected_devices:
                self.connected_devices[device_id]["is_trusted"] = True
            
            if success:
                self.logger.info(f"✅ Appareil approuvé: {device_id}")
                
                for callback in self._on_device_approved_callbacks:
                    try:
                        callback(device_id)
                    except Exception as e:
                        self.logger.error(f"Erreur callback approve: {e}")
            
            return success
        else:
            # Pas de storage, on approuve juste en mémoire
            if device_id in self.connected_devices:
                self.connected_devices[device_id]["is_trusted"] = True
                self.logger.info(f"✅ Appareil approuvé (en mémoire): {device_id}")
                
                for callback in self._on_device_approved_callbacks:
                    try:
                        callback(device_id)
                    except Exception as e:
                        self.logger.error(f"Erreur callback approve: {e}")
                
                return True
        
        return False
    
    def reject_device(self, device_id: str) -> bool:
        """
        Rejette un appareil (le supprime).
        
        Args:
            device_id: ID de l'appareil à rejeter
        
        Returns:
            True si succès
        """
        if device_id in self.connected_devices:
            del self.connected_devices[device_id]
        
        if self.storage:
            return self.storage.delete_device(device_id)
        
        return True
    
    def is_device_trusted(self, device_id: str) -> bool:
        """
        Vérifie si un appareil est de confiance.
        
        Args:
            device_id: ID de l'appareil
        
        Returns:
            True si trusted
        """
        if device_id in self.connected_devices:
            return self.connected_devices[device_id].get("is_trusted", False)
        
        if self.storage:
            device = self.storage.get_device(device_id)
            if device:
                return bool(device.get("is_trusted", False))
        
        return False
    
    def is_device_connected(self, device_id: str) -> bool:
        """Vérifie si un appareil est actuellement connecté."""
        return device_id in self.connected_devices
    
    def get_connected_devices(self) -> List[dict]:
        """Retourne la liste des appareils connectés."""
        return list(self.connected_devices.values())
    
    def get_device_info(self, device_id: str) -> Optional[dict]:
        """Retourne les infos d'un appareil."""
        if device_id in self.connected_devices:
            return self.connected_devices[device_id]
        
        if self.storage:
            return self.storage.get_device(device_id)
        
        return None
    
    def get_trusted_connected_devices(self) -> List[dict]:
        """Retourne les appareils connectés ET de confiance."""
        return [
            device for device in self.connected_devices.values()
            if device.get("is_trusted", False)
        ]
    
    def on_new_device(self, callback):
        """Enregistre un callback pour les nouveaux appareils."""
        self._on_new_device_callbacks.append(callback)
    
    def on_device_approved(self, callback):
        """Enregistre un callback pour les approbations."""
        self._on_device_approved_callbacks.append(callback)
    
    def get_stats(self) -> dict:
        """Retourne les statistiques."""
        total_connected = len(self.connected_devices)
        trusted_connected = len(self.get_trusted_connected_devices())
        
        return {
            "total_connected": total_connected,
            "trusted_connected": trusted_connected,
            "untrusted_connected": total_connected - trusted_connected,
        }


if __name__ == "__main__":
    print("✅ Device Manager ready")