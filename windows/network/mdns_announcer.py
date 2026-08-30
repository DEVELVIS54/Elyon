"""
CLIPBOARD LAN - Module mDNS Announcer
Annonce le serveur sur le réseau local (Bonjour/mDNS)

PHASE 2: Network (WebSocket + mDNS)
"""

import logging
from typing import Optional
import socket

try:
    from zeroconf import ServiceInfo, Zeroconf
except ImportError:
    raise ImportError("zeroconf not installed. Run: pip install zeroconf==0.132.0")


class MDNSAnnouncer:
    """
    Annonce le serveur Clipboard LAN sur le réseau local via mDNS.
    
    Android peut alors découvrir le serveur automatiquement sans
    avoir besoin de l'adresse IP manuelle.
    
    Responsabilités:
    - Annoncer le serveur sur mDNS (Bonjour)
    - Fournir l'adresse IP et le port
    - Gérer le cycle de vie du service
    """
    
    def __init__(self, device_id: str, device_name: str, 
                 host: str = "0.0.0.0", port: int = 7777):
        """
        Initialise l'annonceur mDNS.
        
        Args:
            device_id: ID unique de l'appareil (ex: "windows-pc-1")
            device_name: Nom lisible de l'appareil (ex: "Mon PC")
            host: Adresse IP à annoncer
            port: Port WebSocket (défaut: 7777)
        """
        self.device_id = device_id
        self.device_name = device_name
        self.host = host
        self.port = port
        
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.service_name = f"ClipboardLAN-{device_id}"
        self.service_type = "_clipboard-lan._tcp.local."
        
        # Logging
        self.logger = logging.getLogger("MDNSAnnouncer")
        self.logger.setLevel(logging.INFO)
    
    def start(self):
        """Lance l'annonceur mDNS."""
        try:
            # Obtenir l'adresse IP locale
            ip_address = self._get_local_ip()
            
            self.logger.info(f"📡 Annonce mDNS: {self.service_name}")
            self.logger.info(f"   IP: {ip_address}")
            self.logger.info(f"   Port: {self.port}")
            
            # Créer le service mDNS
            self.service_info = ServiceInfo(
                self.service_type,
                f"{self.service_name}.{self.service_type}",
                addresses=[self._ip_to_bytes(ip_address)],
                port=self.port,
                properties={
                    "device_id": self.device_id,
                    "device_name": self.device_name,
                    "version": "1.0.0-alpha",
                },
                server=f"{self.device_id}.local."
            )
            
            # Enregistrer le service
            self.zeroconf = Zeroconf()
            self.zeroconf.register_service(self.service_info)
            
            self.logger.info(f"✅ Service mDNS enregistré")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage mDNS: {e}")
            raise
    
    def stop(self):
        """Arrête l'annonceur mDNS."""
        try:
            if self.zeroconf:
                self.zeroconf.unregister_service(self.service_info)
                self.zeroconf.close()
                self.logger.info(f"✅ Service mDNS arrêté")
        except Exception as e:
            self.logger.error(f"Erreur arrêt mDNS: {e}")
    
    @staticmethod
    def _get_local_ip() -> str:
        """
        Obtient l'adresse IP locale de l'interface réseau.
        
        Returns:
            Adresse IP locale (ex: "192.168.1.50")
        """
        try:
            # Se connecter à un serveur DNS public (sans vraiment envoyer)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback: utiliser localhost
            return "127.0.0.1"
    
    @staticmethod
    def _ip_to_bytes(ip: str) -> bytes:
        """
        Convertit une adresse IP en bytes.
        
        Args:
            ip: Adresse IP (ex: "192.168.1.50")
        
        Returns:
            Bytes de l'IP
        """
        return bytes(map(int, ip.split(".")))
    
    def get_info(self) -> dict:
        """Retourne les infos du service mDNS."""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "host": self.host,
            "port": self.port,
            "ip": self._get_local_ip(),
            "status": "active" if self.zeroconf else "inactive",
        }


class MDNSDiscovery:
    """
    Découvre les services mDNS (côté client Android).
    
    Responsabilités:
    - Découvrir les serveurs Clipboard LAN sur le réseau
    - Récupérer l'adresse IP et le port
    - Lister les services disponibles
    """
    
    def __init__(self, service_type: str = "_clipboard-lan._tcp.local.", 
                 timeout: int = 5):
        """
        Initialise la découverte mDNS.
        
        Args:
            service_type: Type de service à découvrir
            timeout: Timeout de découverte (secondes)
        """
        self.service_type = service_type
        self.timeout = timeout
        self.zeroconf: Optional[Zeroconf] = None
        
        self.logger = logging.getLogger("MDNSDiscovery")
        self.logger.setLevel(logging.INFO)
    
    def discover(self) -> list[dict]:
        """
        Découvre les services mDNS disponibles.
        
        Returns:
            Liste des services trouvés
        """
        try:
            from zeroconf import ServiceBrowser, Zeroconf
            
            discovered = []
            
            def on_service_state_change(zeroconf, service_type, name, state_change):
                if state_change.name == "Added":
                    try:
                        info = zeroconf.get_service_info(service_type, name)
                        if info:
                            discovered.append({
                                "name": name,
                                "device_id": info.properties.get(b"device_id", b"").decode(),
                                "device_name": info.properties.get(b"device_name", b"").decode(),
                                "address": info.addresses[0] if info.addresses else None,
                                "port": info.port,
                            })
                    except Exception as e:
                        self.logger.error(f"Erreur info service: {e}")
            
            self.zeroconf = Zeroconf()
            browser = ServiceBrowser(self.zeroconf, self.service_type, 
                                     on_service_state_change)
            
            # Attendre la découverte
            import time
            time.sleep(self.timeout)
            
            self.zeroconf.close()
            
            self.logger.info(f"📡 {len(discovered)} service(s) découvert(s)")
            return discovered
        
        except Exception as e:
            self.logger.error(f"Erreur découverte mDNS: {e}")
            return []
    
    def find_service_by_device_id(self, device_id: str) -> Optional[dict]:
        """
        Trouve un service par ID d'appareil.
        
        Args:
            device_id: ID de l'appareil à chercher
        
        Returns:
            Info du service ou None
        """
        services = self.discover()
        for service in services:
            if service["device_id"] == device_id:
                return service
        return None


# ============================================================================
# Tests locaux
# ============================================================================

if __name__ == "__main__":
    print("🧪 Tests du module mDNS\n")
    
    # Test 1: Initialisation annonceur
    print("1️⃣  Test MDNSAnnouncer")
    announcer = MDNSAnnouncer(
        device_id="windows-pc-1",
        device_name="Mon PC",
        port=7777
    )
    print(f"  ✓ Service: {announcer.service_name}")
    print(f"  ✓ Type: {announcer.service_type}")
    print(f"  ✓ IP locale: {announcer._get_local_ip()}\n")
    
    # Test 2: Info
    print("2️⃣  Test get_info")
    info = announcer.get_info()
    print(f"  ✓ Device ID: {info['device_id']}")
    print(f"  ✓ Device Name: {info['device_name']}")
    print(f"  ✓ Port: {info['port']}")
    print(f"  ✓ Status: {info['status']}\n")
    
    # Test 3: Conversion IP
    print("3️⃣  Test IP conversion")
    ip = "192.168.1.50"
    ip_bytes = announcer._ip_to_bytes(ip)
    print(f"  ✓ IP: {ip}")
    print(f"  ✓ Bytes: {ip_bytes}\n")
    
    # Test 4: Discovery
    print("4️⃣  Test MDNSDiscovery")
    discovery = MDNSDiscovery(timeout=2)
    print(f"  ✓ Service type: {discovery.service_type}")
    print(f"  ✓ Timeout: {discovery.timeout}s\n")
    
    print("✅ Tests mDNS complets!")
    print("\nPour lancer l'annonceur réel:")
    print("  announcer = MDNSAnnouncer('windows-pc-1', 'Mon PC')")
    print("  announcer.start()")