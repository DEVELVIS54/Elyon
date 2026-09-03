"""
CLIPBOARD LAN - WebSocket Server
Serveur WebSocket robuste : heartbeat avec détection de timeout,
limite de taille des messages, arrêt propre.

CHEMIN: windows/network/websocket_server.py
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Callable, Optional

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    raise ImportError("websockets not installed. Run: pip install websockets==12.0")


class WebSocketServer:
    """Serveur WebSocket pour Clipboard LAN."""

    # Heartbeat applicatif : certains réseaux (routeur, NAT mobile)
    # ferment les connexions TCP inactives au bout de ~20-30s. On envoie
    # un PING régulier pour garder les connexions vivantes.
    HEARTBEAT_INTERVAL = 10
    # Si aucun PONG n'est reçu depuis ce délai, la connexion est
    # considérée morte et fermée côté serveur (nettoyage des "clients
    # fantômes" — un socket TCP peut rester ouvert alors que le réseau a
    # déjà coupé sans le signaler).
    HEARTBEAT_TIMEOUT = 30
    # Rejette tout message dépassant cette taille (protection basique
    # contre un client malformé ou malveillant qui saturerait le buffer).
    MAX_MESSAGE_SIZE = 2_000_000  # 2 MB

    def __init__(self, host: str = "0.0.0.0", port: int = 7777):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"

        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self._last_pong: Dict[str, datetime] = {}
        self._connected_since: Dict[str, datetime] = {}

        self._on_message_callbacks: list[Callable] = []
        self._on_connect_callbacks: list[Callable] = []
        self._on_disconnect_callbacks: list[Callable] = []

        self.logger = logging.getLogger("WebSocketServer")
        self.logger.setLevel(logging.INFO)

        self._server = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self):
        """Lance le serveur WebSocket + la boucle de heartbeat."""
        self.logger.info(f"🚀 Serveur WebSocket sur {self.uri}")

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        try:
            self._server = await websockets.serve(
                self._handle_client, self.host, self.port,
                ping_interval=None,  # on gère notre propre heartbeat applicatif
                max_size=self.MAX_MESSAGE_SIZE,
            )
            self.logger.info("✅ Serveur actif")
            await asyncio.Future()
        finally:
            self._heartbeat_task.cancel()

    async def stop(self):
        """Arrêt propre : ferme toutes les connexions clients puis le serveur."""
        self.logger.info("🛑 Arrêt du serveur WebSocket")

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        for device_id, ws in list(self.clients.items()):
            try:
                await ws.close(code=1001, reason="Server shutting down")
            except Exception:
                pass

        self.clients.clear()

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        self.logger.info("✅ Serveur arrêté proprement")

    async def _heartbeat_loop(self):
        """
        Envoie un PING à chaque client toutes les HEARTBEAT_INTERVAL
        secondes, et force la déconnexion de tout client n'ayant pas
        répondu depuis plus de HEARTBEAT_TIMEOUT secondes.
        """
        while True:
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

            now = datetime.now()
            stale_devices = []

            for device_id, ws in list(self.clients.items()):
                last_pong = self._last_pong.get(device_id, self._connected_since.get(device_id, now))
                elapsed = (now - last_pong).total_seconds()

                if elapsed > self.HEARTBEAT_TIMEOUT:
                    stale_devices.append(device_id)
                    continue

                try:
                    await ws.send(json.dumps({
                        "type": "PING",
                        "timestamp": now.isoformat()
                    }))
                except Exception as e:
                    self.logger.warning(f"Heartbeat: échec envoi à {device_id}: {e}")
                    stale_devices.append(device_id)

            for device_id in stale_devices:
                self.logger.warning(f"⚠️ Connexion morte détectée (pas de PONG): {device_id}")
                ws = self.clients.pop(device_id, None)
                self._last_pong.pop(device_id, None)
                self._connected_since.pop(device_id, None)

                if ws:
                    try:
                        await ws.close(code=1008, reason="Heartbeat timeout")
                    except Exception:
                        pass

                for callback in self._on_disconnect_callbacks:
                    try:
                        callback(device_id)
                    except Exception as e:
                        self.logger.error(f"Erreur callback disconnect: {e}")

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Gère une connexion client."""
        device_id = None

        try:
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") != "HELLO":
                await websocket.send(json.dumps({"type": "ERROR", "message": "Expected HELLO"}))
                return

            device_id = data.get("device_id")
            device_name = data.get("device_name", "Unknown")

            if not device_id:
                await websocket.send(json.dumps({"type": "ERROR", "message": "device_id required"}))
                return

            now = datetime.now()
            self.clients[device_id] = websocket
            self._last_pong[device_id] = now
            self._connected_since[device_id] = now

            self.logger.info(f"📱 Connecté: {device_name} ({device_id})")

            for callback in self._on_connect_callbacks:
                try:
                    callback(device_id, device_name)
                except Exception as e:
                    self.logger.error(f"Erreur callback connect: {e}")

            await websocket.send(json.dumps({
                "type": "HELLO_ACK",
                "message": "Connected",
                "timestamp": now.isoformat()
            }))

            await self._receive_loop(websocket, device_id)

        except websockets.exceptions.ConnectionClosed:
            pass
        except json.JSONDecodeError:
            self.logger.warning("Message JSON invalide lors du handshake")
        except Exception as e:
            self.logger.error(f"Erreur: {e}")
        finally:
            duration = ""
            if device_id and device_id in self._connected_since:
                elapsed = (datetime.now() - self._connected_since[device_id]).total_seconds()
                duration = f" (connecté {elapsed:.0f}s)"

            if device_id and device_id in self.clients:
                del self.clients[device_id]
                self._last_pong.pop(device_id, None)
                self._connected_since.pop(device_id, None)
                self.logger.info(f"📴 Déconnecté: {device_id}{duration}")

                for callback in self._on_disconnect_callbacks:
                    try:
                        callback(device_id)
                    except Exception as e:
                        self.logger.error(f"Erreur callback disconnect: {e}")

    async def _receive_loop(self, websocket: WebSocketServerProtocol, device_id: str):
        """Boucle de réception des messages."""
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "PONG":
                    self._last_pong[device_id] = datetime.now()
                    continue

                if msg_type == "PING":
                    # Le client peut aussi initier un ping — on répond directement
                    self._last_pong[device_id] = datetime.now()
                    await websocket.send(json.dumps({
                        "type": "PONG", "timestamp": datetime.now().isoformat()
                    }))
                    continue

                # Tout message applicatif reçu compte comme signe de vie
                self._last_pong[device_id] = datetime.now()

                for callback in self._on_message_callbacks:
                    try:
                        callback(device_id, data)
                    except Exception as e:
                        self.logger.error(f"Erreur callback message: {e}")

                await websocket.send(json.dumps({
                    "type": "ACK",
                    "message_id": data.get("message_id"),
                    "timestamp": datetime.now().isoformat()
                }))

            except json.JSONDecodeError:
                self.logger.warning(f"Message JSON invalide de {device_id}")
                try:
                    await websocket.send(json.dumps({"type": "ERROR", "message": "Invalid JSON"}))
                except Exception:
                    pass
            except Exception as e:
                self.logger.error(f"Erreur traitement message: {e}")

    async def broadcast(self, message: dict, exclude_device: Optional[str] = None):
        """Envoie un message à tous les clients."""
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

        for device_id in disconnected:
            self.clients.pop(device_id, None)
            self._last_pong.pop(device_id, None)
            self._connected_since.pop(device_id, None)

    async def send_to_device(self, device_id: str, message: dict) -> bool:
        """Envoie un message à un appareil spécifique."""
        if device_id not in self.clients:
            self.logger.warning(f"Appareil {device_id} non connecté")
            return False

        try:
            await self.clients[device_id].send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Erreur envoi {device_id}: {e}")
            self.clients.pop(device_id, None)
            self._last_pong.pop(device_id, None)
            self._connected_since.pop(device_id, None)
            return False

    def on_message(self, callback: Callable):
        self._on_message_callbacks.append(callback)

    def on_connect(self, callback: Callable):
        self._on_connect_callbacks.append(callback)

    def on_disconnect(self, callback: Callable):
        self._on_disconnect_callbacks.append(callback)

    def get_connected_devices(self) -> list[str]:
        return list(self.clients.keys())

    def get_info(self) -> dict:
        return {
            "uri": self.uri,
            "host": self.host,
            "port": self.port,
            "connected_devices": len(self.clients),
            "devices": list(self.clients.keys()),
        }


if __name__ == "__main__":
    print("✅ WebSocket Server ready (heartbeat + timeout detection)")