"""
CLIPBOARD LAN - Settings Manager
Gère les paramètres utilisateur
"""

import logging
from typing import Optional, Any
import json


class SettingsManager:
    """Gère les paramètres."""
    
    # Paramètres par défaut
    DEFAULTS = {
        "clipboard_poll_interval": 0.5,
        "max_clipboard_size": 1_000_000,
        "enable_history": True,
        "history_retention_days": 30,
        "auto_trust_devices": False,
        "enable_notifications": True,
        "language": "fr",
    }
    
    def __init__(self, db_manager):
        """Initialise le manager."""
        self.db = db_manager
        self.logger = logging.getLogger("SettingsManager")
        self.logger.setLevel(logging.INFO)
        
        self._load_defaults()
    
    def _load_defaults(self):
        """Charge les defaults."""
        for key, value in self.DEFAULTS.items():
            if self.get(key) is None:
                self.set(key, value)
    
    def set(self, key: str, value: Any, value_type: str = None) -> bool:
        """Sauvegarde un paramètre."""
        try:
            if value_type is None:
                if isinstance(value, bool):
                    value_type = "bool"
                elif isinstance(value, int):
                    value_type = "int"
                else:
                    value_type = "string"
            
            # Convertir en string pour stockage
            if isinstance(value, bool):
                value_str = "1" if value else "0"
            else:
                value_str = str(value)
            
            self.db.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, last_modified)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value_str, value_type))
            
            self.db.commit()
            self.logger.info(f"✅ Paramètre sauvegardé: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère un paramètre."""
        try:
            cursor = self.db.execute(
                "SELECT value, type FROM settings WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return self.DEFAULTS.get(key)
            
            value, value_type = row
            
            # Convertir au bon type
            if value_type == "bool":
                return value == "1"
            elif value_type == "int":
                return int(value)
            else:
                return value
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return self.DEFAULTS.get(key)
    
    def get_all(self) -> dict:
        """Récupère tous les paramètres."""
        try:
            cursor = self.db.execute("SELECT key, value, type FROM settings")
            settings = {}
            
            for row in cursor.fetchall():
                key, value, value_type = row
                
                if value_type == "bool":
                    settings[key] = value == "1"
                elif value_type == "int":
                    settings[key] = int(value)
                else:
                    settings[key] = value
            
            return settings
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return {}
    
    def reset_to_defaults(self) -> bool:
        """Réinitialise aux defaults."""
        try:
            self.db.execute("DELETE FROM settings")
            self.db.commit()
            self._load_defaults()
            self.logger.info("✅ Réinitialisation complète")
            return True
        except Exception as e:
            self.logger.error(f"Erreur réinitialisation: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime un paramètre."""
        try:
            self.db.execute("DELETE FROM settings WHERE key = ?", (key,))
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Erreur suppression: {e}")
            return False


if __name__ == "__main__":
    print("✅ Settings Manager ready")