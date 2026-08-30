"""
CLIPBOARD LAN - Protocol Handler
Parser et validation des messages WebSocket
"""

import json
from typing import Dict, Tuple, Optional
from datetime import datetime
import logging


class ProtocolHandler:
    """Gère le protocole de messages Clipboard LAN."""
    
    def __init__(self, security_manager=None):
        """Initialise le handler de protocole."""
        self.security_manager = security_manager
        self.logger = logging.getLogger("ProtocolHandler")
        self.logger.setLevel(logging.INFO)
    
    def create_message(self, message_type: str, content: str = None, 
                      device_id: str = None, **kwargs) -> dict:
        """Crée un message protocole."""
        message = {
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
        }
        
        if content:
            message["content"] = content
        
        message.update(kwargs)
        
        return message
    
    def create_hello(self, device_id: str, device_name: str, 
                    public_key: str) -> dict:
        """Crée un message HELLO."""
        return self.create_message(
            "HELLO",
            device_id=device_id,
            device_name=device_name,
            public_key=public_key
        )
    
    def create_sync(self, device_id: str, content: str, 
                   content_type: str = "text/plain") -> dict:
        """Crée un message SYNC."""
        return self.create_message(
            "SYNC",
            content=content,
            device_id=device_id,
            content_type=content_type
        )
    
    def create_ack(self, message_id: str) -> dict:
        """Crée un message ACK."""
        return self.create_message(
            "ACK",
            message_id=message_id
        )
    
    def create_error(self, error_message: str) -> dict:
        """Crée un message ERROR."""
        return self.create_message(
            "ERROR",
            message=error_message
        )
    
    def create_ping(self) -> dict:
        """Crée un message PING."""
        return self.create_message("PING")
    
    def create_pong(self) -> dict:
        """Crée un message PONG."""
        return self.create_message("PONG")
    
    def validate_message(self, message: dict) -> Tuple[bool, str]:
        """
        Valide un message reçu.
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        # Vérifier type
        if "type" not in message:
            return False, "Missing 'type' field"
        
        message_type = message.get("type")
        
        # Vérifier les champs requis selon le type
        if message_type == "HELLO":
            if not message.get("device_id"):
                return False, "HELLO requires device_id"
            if not message.get("device_name"):
                return False, "HELLO requires device_name"
            if not message.get("public_key"):
                return False, "HELLO requires public_key"
        
        elif message_type == "SYNC":
            if not message.get("content"):
                return False, "SYNC requires content"
            if not message.get("device_id"):
                return False, "SYNC requires device_id"
        
        elif message_type == "ACK":
            if not message.get("message_id"):
                return False, "ACK requires message_id"
        
        elif message_type == "ERROR":
            if not message.get("message"):
                return False, "ERROR requires message"
        
        # Vérifier timestamp
        if "timestamp" not in message:
            return False, "Missing timestamp"
        
        return True, "Valid"
    
    def parse_json(self, json_str: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        Parse un string JSON.
        
        Returns:
            (message: dict or None, error: str or None)
        """
        try:
            message = json.loads(json_str)
            return message, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {str(e)}"
    
    def sign_message(self, message: dict) -> Optional[str]:
        """Signe un message avec HMAC."""
        if not self.security_manager:
            self.logger.warning("Security manager not configured")
            return None
        
        try:
            message_str = json.dumps(message, sort_keys=True)
            signature = self.security_manager.hmac_sign(message_str)
            return signature
        except Exception as e:
            self.logger.error(f"Erreur signature: {e}")
            return None
    
    def verify_message(self, message: dict, signature: str) -> bool:
        """Vérifie la signature d'un message."""
        if not self.security_manager:
            return False
        
        try:
            message_str = json.dumps(message, sort_keys=True)
            return self.security_manager.hmac_verify(message_str, signature)
        except Exception as e:
            self.logger.error(f"Erreur vérification: {e}")
            return False
    
    def get_message_info(self) -> dict:
        """Retourne les infos du protocole."""
        return {
            "protocol_version": "1.0",
            "message_types": ["HELLO", "SYNC", "ACK", "ERROR", "PING", "PONG", "PAIR"],
            "content_types": ["text/plain", "text/html", "text/uri-list"],
            "port": 7777,
            "mdns_service": "_clipboard-lan._tcp.local.",
        }


if __name__ == "__main__":
    print("✅ Protocol Handler ready")