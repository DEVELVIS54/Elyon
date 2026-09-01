"""
CLIPBOARD LAN - Connection Handler
Gère les reconnexions automatiques et le heartbeat

CHEMIN: windows/sync/connection_handler.py
"""

import logging
import time
from enum import Enum
from typing import Optional, Callable
from datetime import datetime


class ConnectionState(Enum):
    """États possibles de la connexion."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class ConnectionHandler:
    """
    Gère l'état de connexion et les reconnexions automatiques.
    
    Responsabilités:
    - Surveiller l'état de connexion (heartbeat)
    - Gérer les tentatives de reconnexion
    - Notifier les changements d'état
    - Backoff exponentiel
    """
    
    def __init__(self, max_retries: int = 10, 
                 initial_retry_delay: float = 1.0,
                 max_retry_delay: float = 300.0,
                 heartbeat_interval: float = 30.0):
        """
        Initialise le ConnectionHandler.
        
        Args:
            max_retries: Nombre maximum de tentatives
            initial_retry_delay: Délai initial entre tentatives (sec)
            max_retry_delay: Délai maximum (sec)
            heartbeat_interval: Intervalle entre pings (sec)
        """
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.heartbeat_interval = heartbeat_interval
        
        self.state = ConnectionState.DISCONNECTED
        self.retry_count = 0
        self.last_ping_time: Optional[datetime] = None
        self.last_pong_time: Optional[datetime] = None
        
        self.logger = logging.getLogger("ConnectionHandler")
        self.logger.setLevel(logging.INFO)
        
        self._on_state_change_callbacks = []
        self._on_reconnected_callbacks = []
        self._on_connection_lost_callbacks = []
    
    def set_connected(self):
        """Marque la connexion comme établie."""
        was_disconnected = self.state != ConnectionState.CONNECTED
        
        self.state = ConnectionState.CONNECTED
        self.retry_count = 0
        self.last_pong_time = datetime.now()
        
        self.logger.info("✅ Connexion établie")
        
        self._notify_state_change()
        
        if was_disconnected:
            for callback in self._on_reconnected_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Erreur callback reconnect: {e}")
    
    def set_disconnected(self, reason: str = "Unknown"):
        """
        Marque la connexion comme perdue.
        
        Args:
            reason: Raison de la déconnexion
        """
        was_connected = self.state == ConnectionState.CONNECTED
        
        self.state = ConnectionState.DISCONNECTED
        self.logger.warning(f"⚠️ Connexion perdue: {reason}")
        
        self._notify_state_change()
        
        if was_connected:
            for callback in self._on_connection_lost_callbacks:
                try:
                    callback(reason)
                except Exception as e:
                    self.logger.error(f"Erreur callback lost: {e}")
    
    def send_ping(self) -> bool:
        """
        Enregistre l'envoi d'un PING.
        
        Returns:
            True si le ping peut être envoyé
        """
        self.last_ping_time = datetime.now()
        return True
    
    def receive_pong(self):
        """Enregistre la réception d'un PONG."""
        self.last_pong_time = datetime.now()
        
        if self.state != ConnectionState.CONNECTED:
            self.set_connected()
    
    def check_heartbeat_timeout(self, timeout: float = 60.0) -> bool:
        """
        Vérifie si le heartbeat a expiré.
        
        Args:
            timeout: Délai avant timeout (sec)
        
        Returns:
            True si timeout dépassé
        """
        if not self.last_pong_time:
            return False
        
        elapsed = (datetime.now() - self.last_pong_time).total_seconds()
        return elapsed > timeout
    
    def start_reconnect(self) -> float:
        """
        Démarre une tentative de reconnexion.
        
        Returns:
            Délai à attendre avant la tentative (sec)
        """
        self.retry_count += 1
        
        if self.retry_count > self.max_retries:
            self.state = ConnectionState.FAILED
            self.logger.error(f"❌ Échec définitif après {self.max_retries} tentatives")
            self._notify_state_change()
            return -1
        
        self.state = ConnectionState.RECONNECTING
        
        # Backoff exponentiel
        delay = min(
            self.initial_retry_delay * (2 ** (self.retry_count - 1)),
            self.max_retry_delay
        )
        
        self.logger.info(
            f"🔄 Tentative reconnexion {self.retry_count}/{self.max_retries} "
            f"(délai: {delay}s)"
        )
        
        self._notify_state_change()
        
        return delay
    
    def reset(self):
        """Réinitialise l'état de connexion."""
        self.state = ConnectionState.DISCONNECTED
        self.retry_count = 0
        self.last_ping_time = None
        self.last_pong_time = None
        self.logger.info("🔄 État de connexion réinitialisé")
    
    def is_connected(self) -> bool:
        """Vérifie si actuellement connecté."""
        return self.state == ConnectionState.CONNECTED
    
    def is_reconnecting(self) -> bool:
        """Vérifie si en cours de reconnexion."""
        return self.state == ConnectionState.RECONNECTING
    
    def has_failed(self) -> bool:
        """Vérifie si la connexion a définitivement échoué."""
        return self.state == ConnectionState.FAILED
    
    def get_status(self) -> dict:
        """Retourne le statut complet."""
        return {
            "state": self.state.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "last_ping": self.last_ping_time.isoformat() if self.last_ping_time else None,
            "last_pong": self.last_pong_time.isoformat() if self.last_pong_time else None,
        }
    
    def on_state_change(self, callback: Callable):
        """Enregistre un callback pour les changements d'état."""
        self._on_state_change_callbacks.append(callback)
    
    def on_reconnected(self, callback: Callable):
        """Enregistre un callback pour les reconnexions réussies."""
        self._on_reconnected_callbacks.append(callback)
    
    def on_connection_lost(self, callback: Callable):
        """Enregistre un callback pour les pertes de connexion."""
        self._on_connection_lost_callbacks.append(callback)
    
    def _notify_state_change(self):
        """Notifie tous les callbacks de changement d'état."""
        for callback in self._on_state_change_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                self.logger.error(f"Erreur callback state change: {e}")


if __name__ == "__main__":
    print("✅ Connection Handler ready")