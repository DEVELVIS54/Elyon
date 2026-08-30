"""
CLIPBOARD LAN - Module WebSocket Server
Serveur WebSocket pour communication avec Android

PHASE 2: Network (WebSocket + mDNS)
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Callable, Optional
from pathlib import Path

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    raise ImportError("websockets not installed. Run: pip install websockets==12.0")


class WebSocketServer:
    """
    Serveur WebSocket pour Clipboard LAN.
    
    Responsabilités:
    - Accepter connexions WebSocket
    - Gérer les clients connectés
    - Router les messages
    - Authentifier les appareils
    - Gérer les déconnexions
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 7777):
        """
        Initialise le serveur WebSocket.
        
        Args:
            host: Adresse à écouter (0.0.0.0 = tous les interfaces)
            port: Port WebSocket (défaut: 7777)
        """
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        
        # Clients connectés: {device_id: WebSocketServerProtocol}
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        
        # Callbacks
        self._on_message_callbacks: list[Callable] = []
        self._on_connect_callbacks: list[Callable] = []
        self._on_disconnect_callbacks: list[Callable] = []
        
        # Logging
        self.logger = logging.getLogger("WebSocketServer")
        self.logger.setLevel(logging.INFO)
    
    async def start(self):
        """Lance le serveur WebSocket."""
        self.logger.info(f"🚀 Démarrage serveur WebSocket sur {self.uri}")
        
        async with websockets.serve(self._handle_client, self.host, self.port):
            self.logger.info(f"✅ Serveur écoute sur {self.uri}")
            await asyncio.Future()  # Tourne indéfiniment
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Gère une connexion client.
        
        Args:
            websocket: Connexion WebSocket
            path: Chemin de connexion
        """
        device_id = None
        
        try:
            # Attendre le message HELLO d'authentification
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("type") != "HELLO":
                await websocket.send(json.dumps({
                    "type": "ERROR",
                    "message": "Expected HELLO message first"
                }))
                return
            
            device_id = data.get("device_id")
            device_name = data.get("device_name", "Unknown")
            
            if not device_id:
                await websocket.send(json.dumps({
                    "type": "ERROR",
                    "message": "device_id required"
                }))
                return
            
            # Enregistrer le client
            self.clients[device_id] = websocket
            self.logger.info(f"📱 Appareil connecté: {device_name} ({device_id})")
            
            # Notifier les callbacks de connexion
            for callback in self._on_connect_callbacks:
                try:
                    callback(device_id, device_name)
                except Exception as e:
                    self.logger.error(f"Erreur callback connect: {e}")
            
            # Envoyer confirmation
            await websocket.send(json.dumps({
                "type": "HELLO_ACK",
                "message": "Connected to Clipboard LAN server",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Boucle de réception
            await self._receive_loop(websocket, device_id)
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Erreur client: {e}")
        finally:
            # Nettoyer
            if device_id and device_id in self.clients:
                del self.clients[device_id]
                self.logger.info(f"📴 Appareil déconnecté: {device_id}")
                
                # Notifier les callbacks de déconnexion
                for callback in self._on_disconnect_callbacks:
                    try:
                        callback(device_id)
                    except Exception as e:
                        self.logger.error(f"Erreur callback disconnect: {e}")
    
    async def _receive_loop(self, websocket: WebSocketServerProtocol, device_id: str):
        """
        Boucle de réception des messages d'un client.
        
        Args:
            websocket: Connexion WebSocket
            device_id: ID de l'appareil
        """
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Notifier les callbacks
                for callback in self._on_message_callbacks:
                    try:
                        callback(device_id, data)
                    except Exception as e:
                        self.logger.error(f"Erreur callback message: {e}")
                
                # Envoyer ACK
                await websocket.send(json.dumps({
                    "type": "ACK",
                    "message_id": data.get("message_id"),
                    "timestamp": datetime.now().isoformat()
                }))
            
            except json.JSONDecodeError:
                self.logger.error(f"Message JSON invalide de {device_id}")
                await websocket.send(json.dumps({
                    "type": "ERROR",
                    "message": "Invalid JSON"
                }))
            except Exception as e:
                self.logger.error(f"Erreur traitement message: {e}")
    
    async def broadcast(self, message: dict, exclude_device: Optional[str] = None):
        """
        Envoie un message à tous les clients.
        
        Args:
            message: Message JSON à envoyer
            exclude_device: ID de l'appareil à exclure (optionnel)
        """
        message_json = json.dumps(message)
        disconnected = []
        
        for device_id, websocket in self.clients.items():
            if exclude_device and device_id == exclude_device:
                continue
            
            try:
                await websocket.send(message_json)
            except Exception as e:
                self.logger.error(f"Erreur envoi {device_id}: {e}")
                disconnected.append(device_id)
        
        # Nettoyer les déconnexions
        for device_id in disconnected:
            if device_id in self.clients:
                del self.clients[device_id]
    
    async def send_to_device(self, device_id: str, message: dict) -> bool:
        """
        Envoie un message à un appareil spécifique.
        
        Args:
            device_id: ID de l'appareil cible
            message: Message JSON
        
        Returns:
            True si succès, False sinon
        """
        if device_id not in self.clients:
            self.logger.warning(f"Appareil {device_id} non connecté")
            return False
        
        try:
            await self.clients[device_id].send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Erreur envoi {device_id}: {e}")
            if device_id in self.clients:
                del self.clients[device_id]
            return False
    
    def on_message(self, callback: Callable):
        """
        Enregistre un callback pour les nouveaux messages.
        
        Args:
            callback: Fonction(device_id: str, message: dict)
        """
        self._on_message_callbacks.append(callback)
    
    def on_connect(self, callback: Callable):
        """
        Enregistre un callback pour les connexions.
        
        Args:
            callback: Fonction(device_id: str, device_name: str)
        """
        self._on_connect_callbacks.append(callback)
    
    def on_disconnect(self, callback: Callable):
        """
        Enregistre un callback pour les déconnexions.
        
        Args:
            callback: Fonction(device_id: str)
        """
        self._on_disconnect_callbacks.append(callback)
    
    def get_connected_devices(self) -> list[str]:
        """Retourne la liste des appareils connectés."""
        return list(self.clients.keys())
    
    def get_info(self) -> dict:
        """Retourne les infos du serveur."""
        return {
            "uri": self.uri,
            "host": self.host,
            "port": self.port,
            "connected_devices": len(self.clients),
            "devices": list(self.clients.keys()),
        }


# ============================================================================
# Tests locaux
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("🧪 Tests du module WebSocketServer\n")
    
    # Test 1: Initialisation
    print("1️⃣  Test initialisation")
    server = WebSocketServer()
    print(f"  ✓ URI: {server.uri}")
    print(f"  ✓ Host: {server.host}")
    print(f"  ✓ Port: {server.port}\n")
    
    # Test 2: Callbacks
    print("2️⃣  Test callbacks")
    
    def on_msg(device_id, message):
        print(f"  • Message de {device_id}: {message.get('type')}")
    
    def on_conn(device_id, device_name):
        print(f"  • Connecté: {device_name} ({device_id})")
    
    def on_disc(device_id):
        print(f"  • Déconnecté: {device_id}")
    
    server.on_message(on_msg)
    server.on_connect(on_conn)
    server.on_disconnect(on_disc)
    
    print(f"  ✓ 3 callbacks enregistrés\n")
    
    # Test 3: Info
    print("3️⃣  Test get_info")
    info = server.get_info()
    print(f"  ✓ Serveur prêt")
    print(f"  ✓ Appareils connectés: {info['connected_devices']}\n")
    
    print("✅ Tests WebSocketServer complets!")
    print("\nPour lancer le serveur réel:")
    print("  server = WebSocketServer()")
    print("  asyncio.run(server.start())")