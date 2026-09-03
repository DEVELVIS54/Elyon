"""
CLIPBOARD LAN - Database Manager
Gère la connexion SQLite et les migrations

CHEMIN: windows/storage/database.py
"""

import sqlite3
import logging
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime


class DatabaseManager:
    """
    Gère la base de données SQLite.

    Thread-safe: l'app tourne avec plusieurs threads actifs (Tkinter en
    thread principal, serveur WebSocket asyncio dans un thread séparé).
    check_same_thread=False autorise l'accès multi-thread, et un verrou
    sérialise les opérations pour éviter toute corruption en cas
    d'écritures concurrentes.
    """

    def __init__(self, db_path: Path = None):
        """Initialise le manager."""
        if db_path is None:
            db_path = Path("windows/data/clipboard_lan.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("DatabaseManager")
        self.logger.setLevel(logging.INFO)

        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()

    def connect(self):
        """Établit la connexion (thread-safe, réutilisable depuis plusieurs threads)."""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path), check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            self.logger.info(f"✅ Connecté à {self.db_path}")
        except Exception as e:
            self.logger.error(f"Erreur connexion: {e}")
            raise

    def disconnect(self):
        """Ferme la connexion."""
        if self.connection:
            self.connection.close()
            self.logger.info("✅ Déconnecté")

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Exécute une requête (sérialisée via verrou)."""
        if not self.connection:
            self.connect()

        try:
            with self._lock:
                if params:
                    return self.connection.execute(query, params)
                return self.connection.execute(query)
        except Exception as e:
            self.logger.error(f"Erreur requête: {e}")
            raise

    def commit(self):
        """Valide les changements (sérialisé via verrou)."""
        if self.connection:
            with self._lock:
                self.connection.commit()

    def migrate(self):
        """Crée les tables si elles n'existent pas."""
        self.connect()

        self.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                device_id TEXT UNIQUE NOT NULL,
                device_name TEXT NOT NULL,
                public_key TEXT NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                is_trusted BOOLEAN DEFAULT 0
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY,
                source_device_id TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content_size INTEGER,
                content_type TEXT,
                sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                type TEXT,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.commit()
        self.logger.info("✅ Migrations complètes")

    def get_db_info(self) -> dict:
        """Retourne les infos de la BD."""
        self.connect()

        cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        return {
            "path": str(self.db_path),
            "exists": self.db_path.exists(),
            "size": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "tables": tables,
        }


if __name__ == "__main__":
    print("✅ Database Manager ready (thread-safe)")