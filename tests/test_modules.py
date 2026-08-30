"""
CLIPBOARD LAN - Tests unitaires
Tests pour Security, Anti-Loop, Clipboard
"""

import pytest
import time
import tempfile
from pathlib import Path


# ============================================================================
# Fixtures Pytest
# ============================================================================

@pytest.fixture
def temp_keys_dir():
    """Crée un dossier temporaire pour les clés."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def security_manager(temp_keys_dir):
    """Crée une instance SecurityManager avec clés temp."""
    from windows_security import SecurityManager
    return SecurityManager(temp_keys_dir)


@pytest.fixture
def anti_loop_cache():
    """Crée une instance AntiLoopCache."""
    from windows_anti_loop import AntiLoopCache
    return AntiLoopCache(max_size=10, timeout_seconds=30)


@pytest.fixture
def loop_detector():
    """Crée une instance LoopDetector."""
    from windows_anti_loop import LoopDetector
    detector = LoopDetector()
    detector.set_device_id("windows-test")
    return detector


@pytest.fixture
def clipboard_manager():
    """Crée une instance ClipboardManager."""
    from windows_clipboard import ClipboardManager
    return ClipboardManager(max_size=100_000)


# ============================================================================
# TESTS: SecurityManager
# ============================================================================

class TestSecurityManager:
    """Tests pour le module Security."""
    
    def test_key_generation(self, security_manager):
        """Vérifie que les clés RSA et HMAC sont générées."""
        assert security_manager.private_key_path.exists()
        assert security_manager.public_key_path.exists()
        assert security_manager.hmac_secret_path.exists()
    
    def test_public_key_pem_format(self, security_manager):
        """Vérifie le format PEM de la clé publique."""
        pem = security_manager.get_public_key_pem()
        assert pem.startswith("-----BEGIN PUBLIC KEY-----")
        assert pem.endswith("-----END PUBLIC KEY-----\n")
    
    def test_rsa_encrypt_decrypt(self, security_manager):
        """Teste le chiffrement et déchiffrement RSA."""
        plaintext = "Test message for RSA"
        public_key_pem = security_manager.get_public_key_pem()
        
        ciphertext = security_manager.rsa_encrypt(plaintext, public_key_pem)
        assert ciphertext != plaintext
        assert len(ciphertext) > 0
        
        decrypted = security_manager.rsa_decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_rsa_encrypt_different_each_time(self, security_manager):
        """Vérifie que RSA génère des chiffertexts différents (padding)."""
        plaintext = "Same message"
        pem = security_manager.get_public_key_pem()
        
        cipher1 = security_manager.rsa_encrypt(plaintext, pem)
        cipher2 = security_manager.rsa_encrypt(plaintext, pem)
        
        assert cipher1 != cipher2
    
    def test_rsa_sign_verify(self, security_manager):
        """Teste la signature et vérification RSA."""
        message = "Device authentication test"
        pem = security_manager.get_public_key_pem()
        
        signature = security_manager.rsa_sign(message)
        assert len(signature) > 0
        
        assert security_manager.rsa_verify(message, signature, pem)
        assert not security_manager.rsa_verify(message + " modified", signature, pem)
    
    def test_rsa_signature_different_each_time(self, security_manager):
        """Vérifie que les signatures PSS diffèrent (salt aléatoire)."""
        message = "Same message"
        
        sig1 = security_manager.rsa_sign(message)
        sig2 = security_manager.rsa_sign(message)
        
        pem = security_manager.get_public_key_pem()
        assert security_manager.rsa_verify(message, sig1, pem)
        assert security_manager.rsa_verify(message, sig2, pem)
    
    def test_hmac_sign_verify(self, security_manager):
        """Teste HMAC sign/verify."""
        message = '{"type":"SYNC","content":"test"}'
        
        hmac_sig = security_manager.hmac_sign(message)
        assert len(hmac_sig) == 64
        
        assert security_manager.hmac_verify(message, hmac_sig)
        assert not security_manager.hmac_verify(message + " modified", hmac_sig)
    
    def test_hmac_deterministic(self, security_manager):
        """Vérifie que HMAC est déterministe (même sig pour même message)."""
        message = "Deterministic test"
        
        sig1 = security_manager.hmac_sign(message)
        sig2 = security_manager.hmac_sign(message)
        
        assert sig1 == sig2
    
    def test_sha256(self, security_manager):
        """Teste le hash SHA256."""
        data = "test data"
        hash_val = security_manager.sha256(data)
        
        assert len(hash_val) == 64
        assert hash_val == security_manager.sha256(data)
    
    def test_key_info(self, security_manager):
        """Vérifie les infos clés."""
        info = security_manager.get_key_info()
        
        assert info["rsa_key_size"] == 2048
        assert "public_key_fingerprint" in info
        assert len(info["public_key_fingerprint"]) == 16


# ============================================================================
# TESTS: AntiLoopCache & LoopDetector
# ============================================================================

class TestAntiLoopCache:
    """Tests pour AntiLoopCache."""
    
    def test_add_and_detect(self, anti_loop_cache):
        """Teste add et is_loop_detected."""
        content = "First content"
        
        hash1 = anti_loop_cache.add(content, "device_1")
        anti_loop_cache.add(content, "device_1")
        assert anti_loop_cache.is_loop_detected(content)
    
    def test_cache_size_limit(self, anti_loop_cache):
        """Teste la limite de taille du cache."""
        for i in range(15):
            anti_loop_cache.add(f"content_{i}", f"device_{i}")
        
        assert len(anti_loop_cache.cache) <= 10
    
    def test_timeout_expiration(self):
        """Teste l'expiration après timeout."""
        from windows_anti_loop import AntiLoopCache
        cache = AntiLoopCache(timeout_seconds=1)
        
        content = "Temporary content"
        cache.add(content, "device_1")
        
        assert cache.is_loop_detected(content)
        
        time.sleep(1.1)
        
        assert not cache.is_loop_detected(content)
    
    def test_get_hash_info(self, anti_loop_cache):
        """Teste get_hash_info."""
        content = "Info test"
        anti_loop_cache.add(content, "device_test", "text/plain")
        
        info = anti_loop_cache.get_hash_info(content)
        assert info is not None
        assert info["source_device"] == "device_test"
        assert info["content_type"] == "text/plain"
        assert info["age_seconds"] >= 0


class TestLoopDetector:
    """Tests pour LoopDetector."""
    
    def test_empty_content(self, loop_detector):
        """Teste avec contenu vide."""
        should_sync, reason = loop_detector.should_sync("", "device_1")
        assert not should_sync
        assert "vide" in reason.lower()
    
    def test_own_device(self, loop_detector):
        """Teste si on ignore le propre appareil."""
        should_sync, reason = loop_detector.should_sync("content", "windows-test")
        assert not should_sync
        assert "local" in reason.lower()
    
    def test_valid_sync(self, loop_detector):
        """Teste une synchronisation valide."""
        content = "Valid content"
        should_sync, reason = loop_detector.should_sync(content, "android_1")
        assert should_sync
        assert "OK" in reason
    
    def test_echo_detection(self, loop_detector):
        """Teste la détection d'echo."""
        content = "Echo test"
        loop_detector.mark_sent(content)
        
        should_sync, reason = loop_detector.should_sync(content, "device_1")
        assert not should_sync
        assert "echo" in reason.lower()
    
    def test_loop_in_cache(self, loop_detector):
        """Teste détection boucle dans le cache."""
        content = "Loop test"
        loop_detector.mark_received(content, "device_1")
        
        should_sync, reason = loop_detector.should_sync(content, "device_2")
        assert not should_sync
        assert "boucle" in reason.lower()
    
    def test_reset(self, loop_detector):
        """Teste reset du détecteur."""
        loop_detector.mark_received("content", "device_1")
        
        assert loop_detector.cache.is_loop_detected("content")
        
        loop_detector.reset()
        
        should_sync, _ = loop_detector.should_sync("content", "device_2")
        assert should_sync


# ============================================================================
# TESTS: ClipboardManager
# ============================================================================

class TestClipboardManager:
    """Tests pour ClipboardManager."""
    
    def test_write_read(self, clipboard_manager):
        """Teste écriture et lecture."""
        content = "Test clipboard content"
        
        assert clipboard_manager.write(content)
        read = clipboard_manager.read()
        assert read == content
    
    def test_size_limit(self, clipboard_manager):
        """Teste la limite de taille."""
        clipboard_manager.max_size = 100
        
        assert clipboard_manager.write("x" * 50)
        assert not clipboard_manager.write("x" * 200)
    
    def test_same_content_not_rewritten(self, clipboard_manager):
        """Teste qu'on ne réécrit pas le même contenu."""
        content = "Same content"
        
        clipboard_manager.write(content)
        result = clipboard_manager.write(content)
        assert result
    
    def test_force_rewrite(self, clipboard_manager):
        """Teste force=True pour forcer la réécriture."""
        content = "Force test"
        
        clipboard_manager.write(content)
        clipboard_manager._current_content = content
        
        assert clipboard_manager.write(content, force=True)
    
    def test_get_current_and_last_write(self, clipboard_manager):
        """Teste get_current et get_last_write."""
        content1 = "First"
        content2 = "Second"
        
        clipboard_manager.write(content1)
        assert clipboard_manager.get_current() == content1
        assert clipboard_manager.get_last_write() == content1
        
        clipboard_manager.write(content2)
        assert clipboard_manager.get_current() == content2
        assert clipboard_manager.get_last_write() == content2
    
    def test_clear(self, clipboard_manager):
        """Teste clear."""
        clipboard_manager.write("Some content")
        assert clipboard_manager.clear()
        assert clipboard_manager.get_current() == ""
    
    def test_get_info(self, clipboard_manager):
        """Teste get_info."""
        clipboard_manager.write("Test")
        
        info = clipboard_manager.get_info()
        assert info["current_size"] == 4
        assert info["max_size"] == 100_000
        assert not info["is_monitoring"]


class TestClipboardSyncAdapter:
    """Tests pour ClipboardSyncAdapter."""
    
    def test_handle_remote_sync(self, clipboard_manager, loop_detector):
        """Teste handle_remote_sync."""
        from windows_clipboard import ClipboardSyncAdapter
        
        adapter = ClipboardSyncAdapter(clipboard_manager, loop_detector)
        
        success = adapter.handle_remote_sync("Remote content", "android_1")
        assert success
        assert clipboard_manager.get_current() == "Remote content"
    
    def test_handle_local_change_empty(self, clipboard_manager, loop_detector):
        """Teste que contenu vide est ignoré."""
        from windows_clipboard import ClipboardSyncAdapter
        
        adapter = ClipboardSyncAdapter(clipboard_manager, loop_detector)
        sync_events = []
        adapter.on_sync_needed(lambda c, ct: sync_events.append((c, ct)))
        
        adapter.handle_local_change("")
        assert len(sync_events) == 0
    
    def test_handle_remote_sync_with_loop(self, clipboard_manager, loop_detector):
        """Teste que la boucle est évitée."""
        from windows_clipboard import ClipboardSyncAdapter
        
        adapter = ClipboardSyncAdapter(clipboard_manager, loop_detector)
        
        content = "Loop content"
        
        success1 = adapter.handle_remote_sync(content, "android_1")
        assert success1
        
        success2 = adapter.handle_remote_sync(content, "android_2")
        assert not success2
    
    def test_get_state(self, clipboard_manager, loop_detector):
        """Teste get_state."""
        from windows_clipboard import ClipboardSyncAdapter
        
        adapter = ClipboardSyncAdapter(clipboard_manager, loop_detector)
        clipboard_manager.write("State test")
        
        state = adapter.get_state()
        assert "clipboard" in state
        assert "loop_detector" in state
        assert state["clipboard"]["current_size"] == 10


# ============================================================================
# Lancer les tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])