"""
CLIPBOARD LAN - Tests Phase 4 (Sync)
Tests pour SyncManager, DeviceManager, ConnectionHandler

CHEMIN: tests/test_sync.py
"""

import pytest
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_module(name, path):
    """Charge un module dynamiquement."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def device_manager():
    """Crée une instance DeviceManager (sans storage)."""
    module = load_module("device_manager", "windows/sync/device_manager.py")
    return module.DeviceManager(devices_storage=None)


@pytest.fixture
def connection_handler():
    """Crée une instance ConnectionHandler."""
    module = load_module("connection_handler", "windows/sync/connection_handler.py")
    return module.ConnectionHandler(max_retries=3, initial_retry_delay=0.1)


@pytest.fixture
def sync_manager():
    """Crée une instance SyncManager (modules minimaux)."""
    module = load_module("sync_manager", "windows/sync/sync_manager.py")
    return module.SyncManager(device_id="windows-test", device_name="Test PC")


# ============================================================================
# TESTS: DeviceManager
# ============================================================================

class TestDeviceManager:
    """Tests pour DeviceManager."""
    
    def test_initialization(self, device_manager):
        """Teste l'initialisation."""
        assert device_manager.connected_devices == {}
    
    def test_handle_device_connect_new(self, device_manager):
        """Teste connexion d'un nouvel appareil."""
        info = device_manager.handle_device_connect(
            "android-1", "Mon Téléphone", "KEY123"
        )
        
        assert info["device_id"] == "android-1"
        assert info["device_name"] == "Mon Téléphone"
        assert "android-1" in device_manager.connected_devices
    
    def test_handle_device_disconnect(self, device_manager):
        """Teste déconnexion d'un appareil."""
        device_manager.handle_device_connect("android-1", "Phone", "KEY1")
        assert device_manager.is_device_connected("android-1")
        
        device_manager.handle_device_disconnect("android-1")
        assert not device_manager.is_device_connected("android-1")
    
    def test_is_device_connected(self, device_manager):
        """Teste is_device_connected."""
        assert not device_manager.is_device_connected("unknown")
        
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        assert device_manager.is_device_connected("dev1")
    
    def test_get_connected_devices(self, device_manager):
        """Teste get_connected_devices."""
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        device_manager.handle_device_connect("dev2", "Device 2", "KEY2")
        
        devices = device_manager.get_connected_devices()
        assert len(devices) == 2
    
    def test_get_device_info(self, device_manager):
        """Teste get_device_info."""
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        
        info = device_manager.get_device_info("dev1")
        assert info is not None
        assert info["device_name"] == "Device 1"
    
    def test_get_device_info_not_found(self, device_manager):
        """Teste get_device_info non trouvé."""
        info = device_manager.get_device_info("unknown")
        assert info is None
    
    def test_get_stats(self, device_manager):
        """Teste get_stats."""
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        
        stats = device_manager.get_stats()
        assert stats["total_connected"] == 1
    
    def test_on_new_device_callback(self, device_manager):
        """Teste le callback new device."""
        new_devices = []
        device_manager.on_new_device(lambda did, dname: new_devices.append(did))
        
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        
        assert "dev1" in new_devices
    
    def test_reject_device(self, device_manager):
        """Teste reject_device."""
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        assert device_manager.is_device_connected("dev1")
        
        device_manager.reject_device("dev1")
        assert not device_manager.is_device_connected("dev1")


# ============================================================================
# TESTS: ConnectionHandler
# ============================================================================

class TestConnectionHandler:
    """Tests pour ConnectionHandler."""
    
    def test_initialization(self, connection_handler):
        """Teste l'initialisation."""
        assert connection_handler.retry_count == 0
        assert not connection_handler.is_connected()
    
    def test_set_connected(self, connection_handler):
        """Teste set_connected."""
        connection_handler.set_connected()
        
        assert connection_handler.is_connected()
        assert connection_handler.retry_count == 0
    
    def test_set_disconnected(self, connection_handler):
        """Teste set_disconnected."""
        connection_handler.set_connected()
        connection_handler.set_disconnected("Test reason")
        
        assert not connection_handler.is_connected()
    
    def test_send_ping(self, connection_handler):
        """Teste send_ping."""
        result = connection_handler.send_ping()
        assert result is True
        assert connection_handler.last_ping_time is not None
    
    def test_receive_pong(self, connection_handler):
        """Teste receive_pong."""
        connection_handler.receive_pong()
        
        assert connection_handler.last_pong_time is not None
        assert connection_handler.is_connected()
    
    def test_check_heartbeat_timeout_no_pong(self, connection_handler):
        """Teste timeout sans pong."""
        result = connection_handler.check_heartbeat_timeout(timeout=1)
        assert result is False  # Pas de pong = pas de timeout check
    
    def test_check_heartbeat_timeout_expired(self, connection_handler):
        """Teste timeout expiré."""
        connection_handler.receive_pong()
        time.sleep(0.2)
        
        result = connection_handler.check_heartbeat_timeout(timeout=0.1)
        assert result is True
    
    def test_start_reconnect(self, connection_handler):
        """Teste start_reconnect."""
        delay = connection_handler.start_reconnect()
        
        assert delay > 0
        assert connection_handler.retry_count == 1
        assert connection_handler.is_reconnecting()
    
    def test_start_reconnect_max_retries(self, connection_handler):
        """Teste échec après max_retries."""
        for _ in range(3):
            connection_handler.start_reconnect()
        
        delay = connection_handler.start_reconnect()
        
        assert delay == -1
        assert connection_handler.has_failed()
    
    def test_reset(self, connection_handler):
        """Teste reset."""
        connection_handler.set_connected()
        connection_handler.start_reconnect()
        
        connection_handler.reset()
        
        assert connection_handler.retry_count == 0
        assert not connection_handler.is_connected()
    
    def test_get_status(self, connection_handler):
        """Teste get_status."""
        connection_handler.set_connected()
        
        status = connection_handler.get_status()
        assert status["state"] == "connected"
        assert status["retry_count"] == 0
    
    def test_on_reconnected_callback(self, connection_handler):
        """Teste le callback de reconnexion."""
        reconnected = []
        connection_handler.on_reconnected(lambda: reconnected.append(True))
        
        connection_handler.set_disconnected("test")
        connection_handler.set_connected()
        
        assert len(reconnected) == 1
    
    def test_on_connection_lost_callback(self, connection_handler):
        """Teste le callback de perte de connexion."""
        lost = []
        connection_handler.on_connection_lost(lambda reason: lost.append(reason))
        
        connection_handler.set_connected()
        connection_handler.set_disconnected("Network error")
        
        assert len(lost) == 1
        assert lost[0] == "Network error"


# ============================================================================
# TESTS: SyncManager
# ============================================================================

class TestSyncManager:
    """Tests pour SyncManager."""
    
    def test_initialization(self, sync_manager):
        """Teste l'initialisation."""
        assert sync_manager.device_id == "windows-test"
        assert sync_manager.device_name == "Test PC"
        assert not sync_manager.is_running
    
    def test_start_without_modules(self, sync_manager):
        """Teste start sans modules configurés."""
        sync_manager.start()
        assert sync_manager.is_running
    
    def test_stop(self, sync_manager):
        """Teste stop."""
        sync_manager.start()
        sync_manager.stop()
        assert not sync_manager.is_running
    
    def test_get_status(self, sync_manager):
        """Teste get_status."""
        status = sync_manager.get_status()
        
        assert status["device_id"] == "windows-test"
        assert status["device_name"] == "Test PC"
        assert "timestamp" in status
    
    def test_on_sync_callback(self, sync_manager):
        """Teste l'enregistrement de callback sync."""
        events = []
        sync_manager.on_sync(lambda did, content: events.append((did, content)))
        
        assert len(sync_manager._on_sync_callbacks) == 1
    
    def test_on_device_connected_callback(self, sync_manager):
        """Teste callback device connected."""
        events = []
        sync_manager.on_device_connected(lambda did, dname: events.append(did))
        
        sync_manager._handle_device_connect("dev1", "Device 1")
        
        assert "dev1" in events
    
    def test_on_device_disconnected_callback(self, sync_manager):
        """Teste callback device disconnected."""
        events = []
        sync_manager.on_device_disconnected(lambda did: events.append(did))
        
        sync_manager._handle_device_disconnect("dev1")
        
        assert "dev1" in events
    
    def test_handle_sync_message_without_modules(self, sync_manager):
        """Teste handle_sync_message sans modules (ne doit pas crasher)."""
        message = {
            "type": "SYNC",
            "content": "Test content",
            "content_type": "text/plain"
        }
        
        # Ne doit pas lever d'exception
        sync_manager._handle_sync_message("dev1", message)


# ============================================================================
# TESTS: Integration
# ============================================================================

class TestSyncIntegration:
    """Tests d'intégration Phase 4."""
    
    def test_device_manager_with_connection_handler(self, device_manager, connection_handler):
        """Teste DeviceManager + ConnectionHandler ensemble."""
        # Connexion appareil
        device_manager.handle_device_connect("dev1", "Device 1", "KEY1")
        connection_handler.set_connected()
        
        assert device_manager.is_device_connected("dev1")
        assert connection_handler.is_connected()
        
        # Déconnexion
        device_manager.handle_device_disconnect("dev1")
        connection_handler.set_disconnected("Test")
        
        assert not device_manager.is_device_connected("dev1")
        assert not connection_handler.is_connected()
    
    def test_full_reconnection_flow(self, connection_handler):
        """Teste le flux complet de reconnexion."""
        # Connecté
        connection_handler.set_connected()
        assert connection_handler.is_connected()
        
        # Perte de connexion
        connection_handler.set_disconnected("Network lost")
        assert not connection_handler.is_connected()
        
        # Tentative de reconnexion
        delay1 = connection_handler.start_reconnect()
        assert delay1 > 0
        
        # Reconnecté
        connection_handler.set_connected()
        assert connection_handler.is_connected()
        assert connection_handler.retry_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])