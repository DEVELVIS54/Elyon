"""
CLIPBOARD LAN - Module Anti-Loop
Prévention des boucles de synchronisation avec SHA256.

PHASE 2: Clipboard + Anti-loop
"""

import hashlib
import time
from collections import OrderedDict
from typing import Optional, Tuple
from datetime import datetime, timedelta


class AntiLoopCache:
    """
    Cache pour détecter et prévenir les boucles de synchronisation.
    
    Stratégie:
    - Calcule SHA256 du contenu clipboard
    - Stocke les hash récents avec timestamp
    - Ignore les contenus identiques reçus dans la fenêtre de temps
    - Nettoie automatiquement les entrées expirées
    """
    
    def __init__(self, max_size: int = 100, timeout_seconds: int = 60):
        """
        Initialise le cache anti-boucle.
        
        Args:
            max_size: Nombre max d'entrées en cache
            timeout_seconds: Durée avant expiration d'une entrée (secondes)
        """
        self.max_size = max_size
        self.timeout_seconds = timeout_seconds
        
        # OrderedDict pour conserver l'ordre FIFO
        # Format: {sha256_hash: (timestamp, source_device, content_type)}
        self.cache: OrderedDict[str, Tuple[float, str, str]] = OrderedDict()
    
    def _sha256_content(self, content: str) -> str:
        """Calcule le SHA256 du contenu."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _cleanup_expired(self):
        """Supprime les entrées expirées."""
        current_time = time.time()
        expired_keys = [
            key for key, (ts, _, _) in self.cache.items()
            if current_time - ts > self.timeout_seconds
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _trim_cache(self):
        """Réduit le cache si dépassement de taille."""
        while len(self.cache) > self.max_size:
            # Supprimer l'entrée la plus ancienne (FIFO)
            self.cache.popitem(last=False)
    
    def add(self, content: str, source_device: str, content_type: str = "text") -> str:
        """
        Ajoute un contenu au cache anti-boucle.
        
        Args:
            content: Contenu du clipboard
            source_device: ID de l'appareil source
            content_type: Type de contenu (text, html, url, etc.)
        
        Returns:
            SHA256 du contenu
        """
        content_hash = self._sha256_content(content)
        current_time = time.time()
        
        self.cache[content_hash] = (current_time, source_device, content_type)
        
        # Nettoyage et trim
        self._cleanup_expired()
        self._trim_cache()
        
        return content_hash
    
    def is_loop_detected(self, content: str) -> bool:
        """
        Détecte si le contenu est une boucle (déjà vu récemment).
        
        Args:
            content: Contenu du clipboard
        
        Returns:
            True si boucle détectée, False sinon
        """
        content_hash = self._sha256_content(content)
        self._cleanup_expired()
        return content_hash in self.cache
    
    def get_hash_info(self, content: str) -> Optional[dict]:
        """
        Retourne les infos sur un hash (debug/monitoring).
        
        Args:
            content: Contenu du clipboard
        
        Returns:
            Dict avec infos ou None si pas trouvé
        """
        content_hash = self._sha256_content(content)
        self._cleanup_expired()
        
        if content_hash not in self.cache:
            return None
        
        timestamp, source_device, content_type = self.cache[content_hash]
        age_seconds = time.time() - timestamp
        
        return {
            "hash": content_hash,
            "source_device": source_device,
            "content_type": content_type,
            "timestamp": timestamp,
            "age_seconds": age_seconds,
            "expired": age_seconds > self.timeout_seconds,
        }
    
    def clear(self):
        """Vide le cache complètement."""
        self.cache.clear()
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du cache."""
        self._cleanup_expired()
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "timeout_seconds": self.timeout_seconds,
            "entries": [
                {
                    "hash": key[:8] + "...",
                    "source_device": source,
                    "age_seconds": time.time() - ts,
                }
                for key, (ts, source, _) in list(self.cache.items())
            ]
        }


class LoopDetector:
    """
    Détecteur de boucles avec logique applicative.
    
    Règles:
    1. Si le contenu exactement identique est reçu dans la même seconde -> BOUCLE
    2. Si le contenu vient du même appareil -> BOUCLE
    3. Si le hash est dans le cache récent -> BOUCLE
    """
    
    def __init__(self, cache_size: int = 100, timeout_seconds: int = 60):
        """Initialise le détecteur."""
        self.cache = AntiLoopCache(cache_size, timeout_seconds)
        self.last_sent_content: Optional[str] = None
        self.last_sent_time: Optional[float] = None
        self.device_id: Optional[str] = None
    
    def set_device_id(self, device_id: str):
        """Configure l'ID de cet appareil."""
        self.device_id = device_id
    
    def should_sync(self, content: str, source_device: str) -> Tuple[bool, str]:
        """
        Détermine si le contenu doit être synchronisé.
        
        Args:
            content: Contenu du clipboard
            source_device: ID de l'appareil source
        
        Returns:
            (should_sync: bool, reason: str)
        """
        
        # Règle 1: Contenu vide
        if not content or not content.strip():
            return False, "Contenu vide"
        
        # Règle 2: C'est notre propre appareil
        if source_device == self.device_id:
            return False, "Source = appareil local"
        
        # Règle 3: C'est le dernier contenu qu'on a envoyé
        if content == self.last_sent_content:
            if self.last_sent_time and (time.time() - self.last_sent_time) < 2:
                return False, "Echo détecté (envoyé il y a < 2s)"
        
        # Règle 4: Boucle dans le cache
        if self.cache.is_loop_detected(content):
            info = self.cache.get_hash_info(content)
            return False, f"Boucle: seen from {info['source_device']} ({info['age_seconds']:.1f}s ago)"
        
        # Pas de boucle détectée
        return True, "OK - Sync"
    
    def mark_sent(self, content: str):
        """
        Marque un contenu comme envoyé (pour echo detection).
        
        Args:
            content: Contenu qu'on vient d'envoyer
        """
        self.last_sent_content = content
        self.last_sent_time = time.time()
    
    def mark_received(self, content: str, source_device: str, content_type: str = "text"):
        """
        Enregistre un contenu reçu pour futur anti-loop.
        
        Args:
            content: Contenu reçu
            source_device: ID de l'appareil source
            content_type: Type de contenu
        """
        self.cache.add(content, source_device, content_type)
    
    def get_stats(self) -> dict:
        """Retourne les stats de détection de boucles."""
        return {
            "device_id": self.device_id,
            "last_sent": {
                "content_preview": (self.last_sent_content[:50] + "...") if self.last_sent_content else None,
                "time_ago_seconds": time.time() - self.last_sent_time if self.last_sent_time else None,
            },
            "cache": self.cache.get_stats(),
        }
    
    def reset(self):
        """Réinitialise complètement le détecteur."""
        self.cache.clear()
        self.last_sent_content = None
        self.last_sent_time = None


# ============================================================================
# Tests locaux
# ============================================================================

if __name__ == "__main__":
    print("🧪 Tests du module Anti-Loop\n")
    
    # Test 1: Anti-Loop Cache basique
    print("1️⃣  Test AntiLoopCache")
    cache = AntiLoopCache(max_size=5, timeout_seconds=10)
    
    content1 = "Hello World"
    hash1 = cache.add(content1, "device_android_1")
    assert not cache.is_loop_detected(content1), "Premierr ajout ne doit pas être boucle"
    print(f"  ✓ Hash: {hash1[:16]}...")
    
    # Même contenu = boucle
    assert cache.is_loop_detected(content1), "Deuxième ajout = boucle"
    print(f"  ✓ Deuxième ajout détecté comme boucle\n")
    
    # Test 2: Expiration
    print("2️⃣  Test expiration (timeout)")
    cache2 = AntiLoopCache(timeout_seconds=1)
    old_content = "Old data"
    cache2.add(old_content, "device_1")
    assert cache2.is_loop_detected(old_content), "Doit être détecté maintenant"
    
    time.sleep(1.1)  # Attendre expiration
    assert not cache2.is_loop_detected(old_content), "Ne doit pas être détecté après expiration"
    print(f"  ✓ Expiration correcte après timeout\n")
    
    # Test 3: LoopDetector avec règles métier
    print("3️⃣  Test LoopDetector (logique applicative)")
    detector = LoopDetector()
    detector.set_device_id("windows-pc-1")
    
    # Test: contenu vide
    should_sync, reason = detector.should_sync("", "android-1")
    assert not should_sync, "Contenu vide ne doit pas syncer"
    print(f"  ✓ Contenu vide: {reason}")
    
    # Test: contenu valide
    content = "Important data"
    should_sync, reason = detector.should_sync(content, "android-1")
    assert should_sync, "Contenu valide doit syncer"
    print(f"  ✓ Contenu valide: {reason}")
    
    # Marquer comme reçu
    detector.mark_received(content, "android-1")
    
    # Même contenu = boucle
    should_sync, reason = detector.should_sync(content, "android-1")
    assert not should_sync, "Contenu reçu ne doit pas être renvoyé"
    print(f"  ✓ Boucle détectée: {reason}\n")
    
    # Test 4: Echo detection
    print("4️⃣  Test Echo detection")
    detector2 = LoopDetector()
    detector2.set_device_id("windows-pc-1")
    
    content = "Data sent"
    detector2.mark_sent(content)
    
    # Juste après l'envoi
    should_sync, reason = detector2.should_sync(content, "android-1")
    assert not should_sync, "Echo doit être détecté"
    print(f"  ✓ Echo détecté: {reason}")
    
    # Après 3 secondes
    time.sleep(3.1)
    should_sync, reason = detector2.should_sync(content, "android-1")
    # Peut ou non être détecté selon la logique (ici sera boucle car dans cache)
    print(f"  ✓ Après 3s: {reason}\n")
    
    # Test 5: Stats
    print("5️⃣  Stats du détecteur")
    detector3 = LoopDetector(cache_size=3)
    detector3.set_device_id("test-device")
    
    for i in range(5):
        detector3.mark_received(f"content_{i}", f"source_{i}")
    
    stats = detector3.get_stats()
    print(f"  ✓ Cache size: {stats['cache']['size']}/{stats['cache']['max_size']}")
    print(f"  ✓ Device ID: {stats['device_id']}")
    print(f"  ✓ Entrées: {len(stats['cache']['entries'])}\n")
    
    print("✅ Tous les tests anti-loop passent!")
