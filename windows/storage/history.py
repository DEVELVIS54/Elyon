"""
CLIPBOARD LAN - History Manager
Gère l'historique des synchronisations
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta


class HistoryManager:
    """Gère l'historique des syncs."""
    
    def __init__(self, db_manager):
        """Initialise le manager."""
        self.db = db_manager
        self.logger = logging.getLogger("HistoryManager")
        self.logger.setLevel(logging.INFO)
    
    def add_sync(self, source_device_id: str, content_hash: str, 
                content_size: int = 0, content_type: str = "text/plain",
                status: str = "success", error_message: str = None) -> bool:
        """Ajoute un sync à l'historique."""
        try:
            self.db.execute("""
                INSERT INTO sync_history 
                (source_device_id, content_hash, content_size, content_type, status, error_message, sync_time)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (source_device_id, content_hash, content_size, content_type, status, error_message))
            
            self.db.commit()
            self.logger.info(f"✅ Sync enregistré: {source_device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur ajout: {e}")
            return False
    
    def get_history(self, limit: int = 100) -> List[dict]:
        """Récupère l'historique (derniers N)."""
        try:
            cursor = self.db.execute(
                "SELECT * FROM sync_history ORDER BY sync_time DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return []
    
    def get_device_history(self, device_id: str, limit: int = 50) -> List[dict]:
        """Récupère l'historique d'un appareil."""
        try:
            cursor = self.db.execute(
                "SELECT * FROM sync_history WHERE source_device_id = ? ORDER BY sync_time DESC LIMIT ?",
                (device_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Récupère les statistiques."""
        try:
            cursor = self.db.execute("SELECT COUNT(*) FROM sync_history")
            total = cursor.fetchone()[0]
            
            cursor = self.db.execute(
                "SELECT COUNT(*) FROM sync_history WHERE status = 'success'"
            )
            success = cursor.fetchone()[0]
            
            cursor = self.db.execute(
                "SELECT COUNT(*) FROM sync_history WHERE status = 'failed'"
            )
            failed = cursor.fetchone()[0]
            
            cursor = self.db.execute(
                "SELECT SUM(content_size) FROM sync_history"
            )
            total_size = cursor.fetchone()[0] or 0
            
            return {
                "total_syncs": total,
                "success_syncs": success,
                "failed_syncs": failed,
                "total_size": total_size,
            }
        except Exception as e:
            self.logger.error(f"Erreur stats: {e}")
            return {}
    
    def clear_old_history(self, days: int = 30) -> int:
        """Supprime l'historique ancien."""
        try:
            cursor = self.db.execute(
                "DELETE FROM sync_history WHERE datetime(sync_time) < datetime('now', '-' || ? || ' days')",
                (days,)
            )
            self.db.commit()
            
            deleted = cursor.rowcount
            self.logger.info(f"✅ {deleted} entrées supprimées")
            return deleted
        except Exception as e:
            self.logger.error(f"Erreur suppression: {e}")
            return 0
    
    def get_last_sync(self, device_id: str) -> Optional[dict]:
        """Récupère le dernier sync d'un appareil."""
        try:
            cursor = self.db.execute(
                "SELECT * FROM sync_history WHERE source_device_id = ? ORDER BY sync_time DESC LIMIT 1",
                (device_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            self.logger.error(f"Erreur récupération: {e}")
            return None


if __name__ == "__main__":
    print("✅ History Manager ready")