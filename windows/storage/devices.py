"""
CLIPBOARD LAN - Devices Manager
Gère les appareils connus et leurs clés
"""

import logging
from typing import Optional, List
from datetime import datetime


class DevicesManager:
    """Gère les appareils connus."""
    
    def __init__(self, db_manager):
        """Initialise le manager."""
        self.db = db_manager
        self.logger = logging.getLogger("DevicesManager")
        self.logger.setLevel(logging.INFO)
    
    def add_device(self, device_id: str, device_name: str, public_key: str) -> bool:
        """Ajoute un appareil."""
        try:
            self.db.execute("""
                INSERT OR REPLACE INTO devices (device_id, device_name, public_key, first_seen)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (device_id, device_name, public_key))
            
            self.db.commit()
            self.logger.info(f"✅ Appareil ajouté: {device_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur ajout: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[dict]:
        """Récupère un appareil."""
        try:
            cursor = self.db.execute(
                "SELECT * FROM devices WHERE device_id = ?",
                (device_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return None
    
    def get_all_devices(self) -> List[dict]:
        """Récupère tous les appareils."""
        try:
            cursor = self.db.execute("SELECT * FROM devices")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Erreur liste: {e}")
            return []
    
    def delete_device(self, device_id: str) -> bool:
        """Supprime un appareil."""
        try:
            self.db.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
            self.db.commit()
            self.logger.info(f"✅ Appareil supprimé: {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur suppression: {e}")
            return False
    
    def trust_device(self, device_id: str) -> bool:
        """Marque un appareil comme de confiance."""
        try:
            self.db.execute(
                "UPDATE devices SET is_trusted = 1, last_seen = CURRENT_TIMESTAMP WHERE device_id = ?",
                (device_id,)
            )
            self.db.commit()
            self.logger.info(f"✅ Appareil approuvé: {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur approbation: {e}")
            return False
    
    def get_public_key(self, device_id: str) -> Optional[str]:
        """Récupère la clé publique d'un appareil."""
        device = self.get_device(device_id)
        if device:
            return device.get("public_key")
        return None
    
    def update_last_seen(self, device_id: str) -> bool:
        """Met à jour le dernier accès."""
        try:
            self.db.execute(
                "UPDATE devices SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?",
                (device_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Erreur update: {e}")
            return False
    
    def get_trusted_devices(self) -> List[dict]:
        """Récupère les appareils de confiance."""
        try:
            cursor = self.db.execute("SELECT * FROM devices WHERE is_trusted = 1")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return []


if __name__ == "__main__":
    print("✅ Devices Manager ready")