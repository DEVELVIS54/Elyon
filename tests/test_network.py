"""
CLIPBOARD LAN - Tests Phase 2 (Network)
Tests pour WebSocket Server, mDNS Announcer, Protocol Handler
"""

import pytest
import json
import asyncio
from datetime import datetime
from pathlib import Path


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def protocol_handler():
    """Crée une instance ProtocolHandler."""
    from windows.network.protocol import ProtocolHandler
    return ProtocolHandler()


@pytest.fixture
def mdns_announcer():
    """Crée une instance MDNSAnnouncer."""
    from windows.network.mdns_announcer import MDNSAnnouncer
    return MDNSAnnouncer(
        device_id="windows-pc-1",
        device_name="Test PC",
        port=7777
    )


@pytest.fixture
def mdns_discovery():
    """Crée une instance MDNSDiscovery."""
    from windows.network.mdns_announcer import MDNSDiscovery
    return MDNSDiscovery(timeout=2)


# ============================================================================
# TESTS: ProtocolHandler
# ============================================================================

class TestProtocolHandler:
    """Tests pour le ProtocolHandler."""
    
    def test_initialization(self, protocol_handler):
        """Teste l'initialisation."""
        assert protocol_handler.security_manager is None
        assert protocol_handler.logger is not None
    
    def test_create_message(self, protocol_handler):
        """Teste la création d'un message."""
        message = protocol_handler.create_message("HELLO", device_id="test")
        
        assert message["type"] == "HELLO"
        assert message["device_id"] == "test"
        assert "timestamp" in message
    
    def test_create_hello(self, protocol_handler):
        """Teste create_hello."""
        message = protocol_handler.create_hello(
            device_id="android-1",
            device_name="Mon Téléphone",
            public_key="ABC123"
        )
        
        assert message["type"] == "HELLO"
        assert message["device_id"] == "android-1"
        assert message["device_name"] == "Mon Téléphone"
        assert message["public_key"] == "ABC123"
    
    def test_create_sync(self, protocol_handler):
        """Teste create_sync."""
        message = protocol_handler.create_sync(
            device_id="android-1",
            content="Hello World"
        )
        
        assert message["type"] == "SYNC"
        assert message["content"] == "Hello World"
        assert message["content_type"] == "text/plain"
    
    def test_create_ack(self, protocol_handler):
        """Teste create_ack."""
        message = protocol_handler.create_ack(message_id="msg-123")
        
        assert message["type"] == "ACK"
        assert message["message_id"] == "msg-123"
    
    def test_create_error(self, protocol_handler):
        """Teste create_error."""
        message = protocol_handler.create_error("Something went wrong")
        
        assert message["type"] == "ERROR"
        assert message["message"] == "Something went wrong"
    
    def test_create_ping(self, protocol_handler):
        """Teste create_ping."""
        message = protocol_handler.create_ping()
        assert message["type"] == "PING"
    
    def test_create_pong(self, protocol_handler):
        """Teste create_pong."""
        message = protocol_handler.create_pong()
        assert message["type"] == "PONG"
    
    def test_validate_message_valid_hello(self, protocol_handler):
        """Teste validation d'un HELLO valide."""
        message = {
            "type": "HELLO",
            "device_id": "android-1",
            "device_name": "Phone",
            "public_key": "ABC123",
            "timestamp": datetime.now().isoformat()
        }
        
        valid, reason = protocol_handler.validate_message(message)
        assert valid
        assert reason == "Valid"
    
    def test_validate_message_invalid_no_type(self, protocol_handler):
        """Teste validation sans type."""
        message = {"timestamp": datetime.now().isoformat()}
        
        valid, reason = protocol_handler.validate_message(message)
        assert not valid
        assert "type" in reason.lower()
    
    def test_validate_message_invalid_hello_no_device_id(self, protocol_handler):
        """Teste validation HELLO sans device_id."""
        message = {
            "type": "HELLO",
            "device_name": "Phone",
            "public_key": "ABC123",
            "timestamp": datetime.now().isoformat()
        }
        
        valid, reason = protocol_handler.validate_message(message)
        assert not valid
        assert "device_id" in reason.lower()
    
    def test_validate_message_valid_sync(self, protocol_handler):
        """Teste validation d'un SYNC valide."""
        message = {
            "type": "SYNC",
            "device_id": "android-1",
            "content": "Hello World",
            "timestamp": datetime.now().isoformat()
        }
        
        valid, reason = protocol_handler.validate_message(message)
        assert valid
    
    def test_validate_message_invalid_sync_no_content(self, protocol_handler):
        """Teste validation SYNC sans content."""
        message = {
            "type": "SYNC",
            "device_id": "android-1",
            "timestamp": datetime.now().isoformat()
        }
        
        valid, reason = protocol_handler.validate_message(message)
        assert not valid
        assert "content" in reason.lower()
    
    def test_parse_json_valid(self, protocol_handler):
        """Teste parsing d'un JSON valide."""
        json_str = '{"type": "HELLO", "device_id": "test"}'
        
        message, error = protocol_handler.parse_json(json_str)
        assert message is not None
        assert error is None
        assert message["type"] == "HELLO"
    
    def test_parse_json_invalid(self, protocol_handler):
        """Teste parsing d'un JSON invalide."""
        json_str = '{invalid json}'
        
        message, error = protocol_handler.parse_json(json_str)
        assert message is None
        assert error is not None
        assert "JSON" in error
    
    def test_get_message_info(self, protocol_handler):
        """Teste get_message_info."""
        info = protocol_handler.get_message_info()
        
        assert info["protocol_version"] == "1.0"
        assert "HELLO" in info["message_types"]
        assert "SYNC" in info["message_types"]
        assert "ACK" in info["message_types"]
        assert info["port"] == 7777


# ============================================================================
# TESTS: MDNSAnnouncer
# ============================================================================

class TestMDNSAnnouncer:
    """Tests pour MDNSAnnouncer."""
    
    def test_initialization(self, mdns_announcer):
        """Teste l'initialisation."""
        assert mdns_announcer.device_id == "windows-pc-1"
        assert mdns_announcer.device_name == "Test PC"
        assert mdns_announcer.port == 7777
        assert mdns_announcer.zeroconf is None
    
    def test_service_name(self, mdns_announcer):
        """Teste le nom du service."""
        assert "ClipboardLAN" in mdns_announcer.service_name
        assert "windows-pc-1" in mdns_announcer.service_name
    
    def test_service_type(self, mdns_announcer):
        """Teste le type de service."""
        assert mdns_announcer.service_type == "_clipboard-lan._tcp.local."
    
    def test_get_local_ip(self, mdns_announcer):
        """Teste get_local_ip."""
        ip = mdns_announcer._get_local_ip()
        
        # Doit retourner une IP valide ou localhost
        assert ip is not None
        assert isinstance(ip, str)
        assert "." in ip
    
    def test_ip_to_bytes(self, mdns_announcer):
        """Teste conversion IP en bytes."""
        ip = "192.168.1.50"
        ip_bytes = mdns_announcer._ip_to_bytes(ip)
        
        assert isinstance(ip_bytes, bytes)
        assert len(ip_bytes) == 4
        assert ip_bytes == b'\xc0\xa8\x01\x32'
    
    def test_get_info(self, mdns_announcer):
        """Teste get_info."""
        info = mdns_announcer.get_info()
        
        assert info["device_id"] == "windows-pc-1"
        assert info["device_name"] == "Test PC"
        assert info["port"] == 7777
        assert "service_name" in info
        assert "service_type" in info
        assert "ip" in info
        assert info["status"] == "inactive"  # Pas encore lancé


# ============================================================================
# TESTS: MDNSDiscovery
# ============================================================================

class TestMDNSDiscovery:
    """Tests pour MDNSDiscovery."""
    
    def test_initialization(self, mdns_discovery):
        """Teste l'initialisation."""
        assert mdns_discovery.service_type == "_clipboard-lan._tcp.local."
        assert mdns_discovery.timeout == 2
        assert mdns_discovery.zeroconf is None
    
    def test_discover_returns_list(self, mdns_discovery):
        """Teste que discover retourne une liste."""
        # Note: Ce test ne trouvera rien sans serveur réel
        # mais vérifie que la méthode fonctionne
        services = mdns_discovery.discover()
        
        assert isinstance(services, list)
    
    def test_find_service_by_device_id_returns_none_if_not_found(self, mdns_discovery):
        """Teste find_service_by_device_id quand pas trouvé."""
        # Note: Pas de serveur réel donc retourne None
        service = mdns_discovery.find_service_by_device_id("nonexistent")
        
        # Soit None soit une liste vide
        assert service is None or service == []


# ============================================================================
# TESTS: Integration
# ============================================================================

class TestIntegration:
    """Tests d'intégration Phase 2."""
    
    def test_protocol_message_roundtrip(self, protocol_handler):
        """Teste création → parse → validation."""
        # Créer un message
        original = protocol_handler.create_sync(
            device_id="android-1",
            content="Test content"
        )
        
        # Convertir en JSON
        json_str = json.dumps(original)
        
        # Parser
        parsed, error = protocol_handler.parse_json(json_str)
        assert error is None
        
        # Valider
        valid, reason = protocol_handler.validate_message(parsed)
        assert valid
        
        # Vérifier que c'est identique
        assert parsed["type"] == original["type"]
        assert parsed["content"] == original["content"]
    
    def test_mdns_announcer_ip_handling(self, mdns_announcer):
        """Teste la gestion des IPs."""
        ip = mdns_announcer._get_local_ip()
        ip_bytes = mdns_announcer._ip_to_bytes(ip)
        
        # Vérifier conversion
        assert isinstance(ip_bytes, bytes)
        assert len(ip_bytes) == 4
    
    def test_protocol_multiple_message_types(self, protocol_handler):
        """Teste création de plusieurs types de messages."""
        messages = [
            protocol_handler.create_hello("dev1", "Device 1", "key1"),
            protocol_handler.create_sync("dev1", "content1"),
            protocol_handler.create_ack("msg1"),
            protocol_handler.create_error("error"),
            protocol_handler.create_ping(),
            protocol_handler.create_pong(),
        ]
        
        expected_types = ["HELLO", "SYNC", "ACK", "ERROR", "PING", "PONG"]
        
        for message, expected_type in zip(messages, expected_types):
            assert message["type"] == expected_type
            assert "timestamp" in message


# ============================================================================
# Tests simples sans async
# ============================================================================

class TestWebSocketServerBasic:
    """Tests basiques pour WebSocketServer (sans async)."""
    
    def test_websocket_server_initialization(self):
        """Teste l'initialisation du serveur."""
        from windows.network.websocket_server import WebSocketServer
        
        server = WebSocketServer(host="0.0.0.0", port=7777)
        
        assert server.host == "0.0.0.0"
        assert server.port == 7777
        assert server.uri == "ws://0.0.0.0:7777"
        assert len(server.clients) == 0
    
    def test_websocket_server_get_info(self):
        """Teste get_info du serveur."""
        from windows.network.websocket_server import WebSocketServer
        
        server = WebSocketServer()
        info = server.get_info()
        
        assert info["port"] == 7777
        assert info["connected_devices"] == 0
        assert isinstance(info["devices"], list)
    
    def test_websocket_server_callback_registration(self):
        """Teste l'enregistrement des callbacks."""
        from windows.network.websocket_server import WebSocketServer
        
        server = WebSocketServer()
        
        def dummy_callback(*args):
            pass
        
        server.on_message(dummy_callback)
        server.on_connect(dummy_callback)
        server.on_disconnect(dummy_callback)
        
        assert len(server._on_message_callbacks) == 1
        assert len(server._on_connect_callbacks) == 1
        assert len(server._on_disconnect_callbacks) == 1


# ============================================================================
# Lancer les tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])