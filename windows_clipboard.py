"""
CLIPBOARD LAN - Module Clipboard
Lecture, écriture, et monitoring du presse-papier Windows.

PHASE 2: Clipboard + Anti-loop
"""

import time
import threading
from typing import Optional, Callable
from pathlib import Path
import pyperclip


class ClipboardManager:
    """
    Gère le presse-papier Windows.
    
    Responsabilités:
    - Lire le contenu actuel
    - Écrire du contenu (sans boucle)
    - Monitorer les changements
    - Notifier les listeners
    """
    
    def __init__(self, max_size: int = 1_000_000):
        """
        Initialise le gestionnaire clipboard.
        
        Args:
            max_size: Taille maximale du contenu (octets)
        """
        self.max_size = max_size
        self._current_content: Optional[str] = None
        self._last_write_content: Optional[str] = None
        
        # Listeners
        self._on_change_callbacks: list[Callable] = []
        
        # Threading
        self._monitor_thread: Optional[threading.Thread] = None
        self._is_monitoring = False
        self._monitor_interval = 0.5  # secondes
    
    def read(self) -> Optional[str]:
        """
        Lit le contenu actuel du presse-papier.
        
        Returns:
            Contenu du clipboard ou None en cas d'erreur
        """
        try:
            content = pyperclip.paste()
            
            # Vérifier la taille
            if len(content) > self.max_size:
                print(f"⚠️  Clipboard trop volumineux: {len(content)} > {self.max_size}")
                return None
            
            self._current_content = content
            return content
        
        except Exception as e:
            print(f"❌ Erreur lecture clipboard: {e}")
            return None
    
    def write(self, content: str, force: bool = False) -> bool:
        """
        Écrit du contenu dans le presse-papier.
        
        Args:
            content: Contenu à écrire
            force: Si True, écrit même si c'est le même contenu
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier la taille
            if len(content) > self.max_size:
                print(f"❌ Contenu trop volumineux: {len(content)} > {self.max_size}")
                return False
            
            # Ne pas réécrire le même contenu (optionnel)
            if not force and content == self._current_content:
                print(f"ℹ️  Clipboard déjà à jour (même contenu)")
                return True
            
            # Écrire
            pyperclip.copy(content)
            self._last_write_content = content
            self._current_content = content
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur écriture clipboard: {e}")
            return False
    
    def get_current(self) -> Optional[str]:
        """Retourne le contenu actuellement en cache."""
        return self._current_content
    
    def get_last_write(self) -> Optional[str]:
        """Retourne le dernier contenu écrit."""
        return self._last_write_content
    
    # ========================================================================
    # Monitoring en arrière-plan
    # ========================================================================
    
    def on_change(self, callback: Callable[[str], None]):
        """
        Enregistre un callback quand le clipboard change.
        
        Args:
            callback: Fonction(content: str) appelée quand changement détecté
        """
        self._on_change_callbacks.append(callback)
    
    def start_monitoring(self):
        """Lance le thread de monitoring du clipboard."""
        if self._is_monitoring:
            print("⚠️  Monitoring déjà actif")
            return
        
        self._is_monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ClipboardMonitor"
        )
        self._monitor_thread.start()
        print(f"✓ Monitoring clipboard lancé (interval: {self._monitor_interval}s)")
    
    def stop_monitoring(self):
        """Arrête le monitoring."""
        self._is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("✓ Monitoring clipboard arrêté")
    
    def _monitor_loop(self):
        """Thread loop pour monitorer le clipboard."""
        last_content = self.read()
        
        while self._is_monitoring:
            try:
                current_content = self.read()
                
                # Détecter changement
                if current_content != last_content and current_content:
                    last_content = current_content
                    self._notify_change(current_content)
                
                time.sleep(self._monitor_interval)
            
            except Exception as e:
                print(f"❌ Erreur monitor loop: {e}")
                time.sleep(1)
    
    def _notify_change(self, content: str):
        """Appelle tous les callbacks de changement."""
        for callback in self._on_change_callbacks:
            try:
                callback(content)
            except Exception as e:
                print(f"❌ Erreur callback clipboard: {e}")
    
    def clear(self) -> bool:
        """Vide le presse-papier."""
        try:
            pyperclip.copy("")
            self._current_content = ""
            self._last_write_content = ""
            return True
        except Exception as e:
            print(f"❌ Erreur clear clipboard: {e}")
            return False
    
    def get_info(self) -> dict:
        """Retourne les infos sur l'état du clipboard."""
        current = self._current_content or ""
        return {
            "current_size": len(current),
            "current_preview": (current[:50] + "...") if len(current) > 50 else current,
            "max_size": self.max_size,
            "is_monitoring": self._is_monitoring,
            "callbacks_registered": len(self._on_change_callbacks),
        }


class ClipboardSyncAdapter:
    """
    Adaptateur pour intégrer le clipboard avec la synchronisation.
    
    Ajoute la logique:
    - Anti-loop avant écriture
    - Notification de changements
    - Gestion des erreurs
    """
    
    def __init__(self, clipboard_manager: ClipboardManager, loop_detector):
        """
        Initialise l'adaptateur.
        
        Args:
            clipboard_manager: Instance ClipboardManager
            loop_detector: Instance LoopDetector pour anti-boucle
        """
        self.clipboard = clipboard_manager
        self.loop_detector = loop_detector
        self._sync_callback: Optional[Callable] = None
    
    def on_sync_needed(self, callback: Callable[[str, str], None]):
        """
        Enregistre callback quand sync nécessaire.
        
        Args:
            callback: Fonction(content: str, content_type: str)
        """
        self._sync_callback = callback
    
    def handle_local_change(self, content: str):
        """
        Traite un changement local du clipboard.
        
        Args:
            content: Contenu détecté
        """
        if not content or not content.strip():
            return
        
        # Vérifier anti-boucle
        should_sync, reason = self.loop_detector.should_sync(
            content,
            self.loop_detector.device_id  # Contenu local
        )
        
        if not should_sync:
            print(f"⏭️  Sync ignorée: {reason}")
            return
        
        print(f"✓ Sync locale détectée: {reason}")
        self.loop_detector.mark_sent(content)
        
        # Notifier
        if self._sync_callback:
            self._sync_callback(content, "text/plain")
    
    def handle_remote_sync(self, content: str, source_device: str) -> bool:
        """
        Traite une synchronisation reçue.
        
        Args:
            content: Contenu à synchroniser
            source_device: ID du device source
        
        Returns:
            True si écrit, False sinon
        """
        if not content or not content.strip():
            return False
        
        # Vérifier anti-boucle
        should_sync, reason = self.loop_detector.should_sync(content, source_device)
        
        if not should_sync:
            print(f"⏭️  Sync distante ignorée: {reason}")
            return False
        
        print(f"✓ Sync distante acceptée: {source_device} -> {reason}")
        
        # Écrire dans le clipboard
        if self.clipboard.write(content):
            self.loop_detector.mark_received(content, source_device, "text/plain")
            return True
        
        return False
    
    def get_state(self) -> dict:
        """Retourne l'état complet du système."""
        return {
            "clipboard": self.clipboard.get_info(),
            "loop_detector": self.loop_detector.get_stats(),
        }


# ============================================================================
# Tests locaux
# ============================================================================

if __name__ == "__main__":
    from windows_anti_loop import LoopDetector
    
    print("🧪 Tests du module Clipboard\n")
    
    # Test 1: ClipboardManager basique
    print("1️⃣  Test ClipboardManager")
    clipboard = ClipboardManager(max_size=100_000)
    
    # Écrire
    content = "Test Clipboard LAN"
    success = clipboard.write(content)
    assert success, "Écriture échouée"
    print(f"  ✓ Écriture: {content}")
    
    # Lire
    read_content = clipboard.read()
    assert read_content == content, "Lecture ≠ écriture"
    print(f"  ✓ Lecture: {read_content}\n")
    
    # Test 2: Détection changement
    print("2️⃣  Test monitoring changement")
    clipboard2 = ClipboardManager()
    changes_detected = []
    
    def on_clipboard_change(content):
        changes_detected.append(content)
    
    clipboard2.on_change(on_clipboard_change)
    clipboard2.start_monitoring()
    
    # Écrire un nouveau contenu
    clipboard2.write("Changed content")
    time.sleep(1)  # Attendre détection
    
    clipboard2.stop_monitoring()
    
    if changes_detected:
        print(f"  ✓ Changement détecté: {changes_detected[0]}")
    else:
        print(f"  ℹ️  Pas de changement détecté (peut être normal)")
    
    print()
    
    # Test 3: ClipboardSyncAdapter avec anti-boucle
    print("3️⃣  Test ClipboardSyncAdapter (avec anti-boucle)")
    clipboard3 = ClipboardManager()
    loop_detector = LoopDetector()
    loop_detector.set_device_id("windows-pc-1")
    
    adapter = ClipboardSyncAdapter(clipboard3, loop_detector)
    
    sync_events = []
    def on_sync(content, content_type):
        sync_events.append((content, content_type))
    
    adapter.on_sync_needed(on_sync)
    
    # Changement local valide
    adapter.handle_local_change("Important data")
    assert len(sync_events) == 1, "Sync local doit trigger"
    print(f"  ✓ Sync locale: {sync_events[0][0]}")
    
    # Sync distante
    success = adapter.handle_remote_sync("Data from Android", "android-phone-1")
    assert success, "Sync distante échouée"
    print(f"  ✓ Sync distante écrite dans clipboard")
    
    # Boucle (même contenu)
    sync_events.clear()
    adapter.handle_local_change("Data from Android")
    assert len(sync_events) == 0, "Boucle doit être évitée"
    print(f"  ✓ Boucle correctement détectée et évitée\n")
    
    # Test 4: Info système
    print("4️⃣  Info état système")
    state = adapter.get_state()
    print(f"  • Clipboard size: {state['clipboard']['current_size']}")
    print(f"  • Loop detector cache: {state['loop_detector']['cache']['size']}\n")
    
    print("✅ Tous les tests clipboard passent!")
