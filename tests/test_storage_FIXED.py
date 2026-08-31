"""
CLIPBOARD LAN - Tests Phase 3 (Storage)
Tests pour Database, Devices, History, Settings
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db_dir():
    """Crée un répertoire temporaire pour la BD."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def db_manager(temp_db_dir):
    """Crée une instance DatabaseManager."""
    # Import direct depuis le fichier
    import importlib.util
    spec = importlib.util.spec_from_file_location("database", "windows/storage/database.py")
    database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    
    DatabaseManager = database_module.DatabaseManager
    db = DatabaseManager(temp_db_dir / "test.db")
    db.migrate()
    yield db
    db.disconnect()


@pytest.fixture
def devices_manager(db_manager):
    """Crée une instance DevicesManager."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("devices", "windows/storage/devices.py")
    devices_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(devices_module)
    
    DevicesManager = devices_module.DevicesManager
    return DevicesManager(db_manager)


@pytest.fixture
def history_manager(db_manager):
    """Crée une instance HistoryManager."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("history", "windows/storage/history.py")
    history_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(history_module)
    
    HistoryManager = history_module.HistoryManager
    return HistoryManager(db_manager)


@pytest.fixture
def settings_manager(db_manager):
    """Crée une instance SettingsManager."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("settings", "windows/storage/settings.py")
    settings_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings_module)
    
    SettingsManager = settings_module.SettingsManager
    return SettingsManager(db_manager)


# ============================================================================
# TESTS: DatabaseManager
# ============================================================================

class TestDatabaseManager:
    """Tests pour DatabaseManager."""
    
    def test_initialization(self, db_manager):
        """Teste l'initialisation."""
        assert db_manager.db_path is not None
        assert db_manager.connection is not None
    
    def test_execute(self, db_manager):
        """Teste execute."""
        cursor = db_manager.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    
    def test_get_db_info(self, db_manager):
        """Teste get_db_info."""
        info = db_manager.get_db_info()
        
        assert info["path"] is not None
        assert info["exists"] is True
        assert "devices" in info["tables"]


# ============================================================================
# TESTS: DevicesManager
# ============================================================================

class TestDevicesManager:
    """Tests pour DevicesManager."""
    
    def test_add_device(self, devices_manager):
        """Teste add_device."""
        result = devices_manager.add_device("android-1", "Mon Téléphone", "ABC123")
        assert result is True
    
    def test_get_device(self, devices_manager):
        """Teste get_device."""
        devices_manager.add_device("android-1", "Phone", "KEY1")
        
        device = devices_manager.get_device("android-1")
        assert device is not None
        assert device["device_id"] == "android-1"
        assert device["device_name"] == "Phone"
    
    def test_get_device_not_found(self, devices_manager):
        """Teste get_device non trouvé."""
        device = devices_manager.get_device("nonexistent")
        assert device is None
    
    def test_get_all_devices(self, devices_manager):
        """Teste get_all_devices."""
        devices_manager.add_device("dev1", "Device 1", "KEY1")
        devices_manager.add_device("dev2", "Device 2", "KEY2")
        
        devices = devices_manager.get_all_devices()
        assert len(devices) >= 2
    
    def test_delete_device(self, devices_manager):
        """Teste delete_device."""
        devices_manager.add_device("dev1", "Device 1", "KEY1")
        
        result = devices_manager.delete_device("dev1")
        assert result is True
        
        device = devices_manager.get_device("dev1")
        assert device is None
    
    def test_trust_device(self, devices_manager):
        """Teste trust_device."""
        devices_manager.add_device("dev1", "Device 1", "KEY1")
        
        result = devices_manager.trust_device("dev1")
        assert result is True
        
        device = devices_manager.get_device("dev1")
        assert device["is_trusted"] == 1
    
    def test_get_public_key(self, devices_manager):
        """Teste get_public_key."""
        devices_manager.add_device("dev1", "Device 1", "ABC123XYZ")
        
        key = devices_manager.get_public_key("dev1")
        assert key == "ABC123XYZ"
    
    def test_update_last_seen(self, devices_manager):
        """Teste update_last_seen."""
        devices_manager.add_device("dev1", "Device 1", "KEY1")
        
        result = devices_manager.update_last_seen("dev1")
        assert result is True
    
    def test_get_trusted_devices(self, devices_manager):
        """Teste get_trusted_devices."""
        devices_manager.add_device("dev1", "Device 1", "KEY1")
        devices_manager.add_device("dev2", "Device 2", "KEY2")
        
        devices_manager.trust_device("dev1")
        
        trusted = devices_manager.get_trusted_devices()
        assert len(trusted) == 1
        assert trusted[0]["device_id"] == "dev1"


# ============================================================================
# TESTS: HistoryManager
# ============================================================================

class TestHistoryManager:
    """Tests pour HistoryManager."""
    
    def test_add_sync(self, history_manager):
        """Teste add_sync."""
        result = history_manager.add_sync("android-1", "hash123", 100, "text/plain")
        assert result is True
    
    def test_get_history(self, history_manager):
        """Teste get_history."""
        history_manager.add_sync("dev1", "hash1", 100)
        history_manager.add_sync("dev2", "hash2", 200)
        
        history = history_manager.get_history()
        assert len(history) >= 2
    
    def test_get_device_history(self, history_manager):
        """Teste get_device_history."""
        history_manager.add_sync("dev1", "hash1", 100)
        history_manager.add_sync("dev1", "hash2", 200)
        history_manager.add_sync("dev2", "hash3", 300)
        
        history = history_manager.get_device_history("dev1")
        assert len(history) == 2
    
    def test_get_stats(self, history_manager):
        """Teste get_stats."""
        history_manager.add_sync("dev1", "hash1", 100, status="success")
        history_manager.add_sync("dev2", "hash2", 200, status="failed")
        
        stats = history_manager.get_stats()
        assert stats["total_syncs"] >= 2
        assert stats["success_syncs"] >= 1
    
    def test_clear_old_history(self, history_manager):
        """Teste clear_old_history."""
        history_manager.add_sync("dev1", "hash1", 100)
        
        deleted = history_manager.clear_old_history(days=-1)
        assert deleted >= 0
    
    def test_get_last_sync(self, history_manager):
        """Teste get_last_sync."""
        history_manager.add_sync("dev1", "hash1", 100)
        history_manager.add_sync("dev1", "hash2", 200)
        
        last = history_manager.get_last_sync("dev1")
        assert last is not None
        assert last["content_hash"] == "hash2"


# ============================================================================
# TESTS: SettingsManager
# ============================================================================

class TestSettingsManager:
    """Tests pour SettingsManager."""
    
    def test_initialization(self, settings_manager):
        """Teste l'initialisation."""
        interval = settings_manager.get("clipboard_poll_interval")
        assert interval is not None
    
    def test_set_and_get(self, settings_manager):
        """Teste set et get."""
        settings_manager.set("test_key", "test_value")
        
        value = settings_manager.get("test_key")
        assert value == "test_value"
    
    def test_set_int(self, settings_manager):
        """Teste set d'un int."""
        settings_manager.set("test_int", 42)
        
        value = settings_manager.get("test_int")
        assert value == 42
    
    def test_set_bool(self, settings_manager):
        """Teste set d'un bool."""
        settings_manager.set("test_bool", True)
        
        value = settings_manager.get("test_bool")
        assert value is True
    
    def test_get_all(self, settings_manager):
        """Teste get_all."""
        settings_manager.set("key1", "value1")
        settings_manager.set("key2", "value2")
        
        all_settings = settings_manager.get_all()
        assert "key1" in all_settings
        assert "key2" in all_settings
    
    def test_reset_to_defaults(self, settings_manager):
        """Teste reset_to_defaults."""
        settings_manager.set("custom_key", "custom_value")
        
        result = settings_manager.reset_to_defaults()
        assert result is True
        
        interval = settings_manager.get("clipboard_poll_interval")
        assert interval is not None
    
    def test_delete(self, settings_manager):
        """Teste delete."""
        settings_manager.set("test_key", "test_value")
        
        result = settings_manager.delete("test_key")
        assert result is True
    
    def test_get_default_values(self, settings_manager):
        """Teste que les defaults sont chargés."""
        interval = settings_manager.get("clipboard_poll_interval")
        max_size = settings_manager.get("max_clipboard_size")
        enable_history = settings_manager.get("enable_history")
        
        assert interval == 0.5
        assert max_size == 1_000_000
        assert enable_history is True


# ============================================================================
# TESTS: Integration
# ============================================================================

class TestStorageIntegration:
    """Tests d'intégration Phase 3."""
    
    def test_full_workflow(self, db_manager, devices_manager, history_manager, settings_manager):
        """Teste le workflow complet."""
        # 1. Ajouter un appareil
        devices_manager.add_device("android-1", "Mon Téléphone", "KEY123")
        
        # 2. Faire un sync
        history_manager.add_sync("android-1", "hash123", 100)
        
        # 3. Paramètres
        settings_manager.set("auto_trust_devices", True)
        
        # 4. Vérifier
        device = devices_manager.get_device("android-1")
        assert device is not None
        
        history = history_manager.get_device_history("android-1")
        assert len(history) == 1
        
        auto_trust = settings_manager.get("auto_trust_devices")
        assert auto_trust is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])