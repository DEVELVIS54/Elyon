"""
CLIPBOARD LAN - GUIDE DE DÉMARRAGE COMPLET
==========================================

Ce guide explique comment démarrer le projet Clipboard LAN à partir de zéro
en évitant les erreurs courantes et en validant chaque étape.
"""

# ============================================================================
# PHASE 0: PRÉPARATION
# ============================================================================

"""
PRÉREQUIS AVANT DE COMMENCER:

✓ Windows 10/11
✓ Python 3.9+ (vérifier: python --version)
✓ Git configuré
✓ ~500MB libre sur disque (pour dépendances)

STRUCTURE:
  Clipboard-LAN/
    ├── windows/           # Composants Windows (Python)
    ├── android/           # Composants Android (Flutter)
    ├── tests/             # Tests unitaires
    ├── docs/              # Documentation
    ├── config.py          # Configuration centralisée ✓
    ├── requirements.txt   # Dépendances ✓
    ├── README.md          # Vue d'ensemble ✓
    └── init_project.py    # Script d'initialisation ✓

FICHIERS FOURNIS:
  ✓ config.py                   - Config centralisée
  ✓ requirements.txt            - Dépendances Python
  ✓ README.md                   - Documentation projet
  ✓ .gitignore                  - Ignore fichiers sensibles
  ✓ init_project.py             - Initialise structure
  ✓ windows_security.py         - Module Security (RSA, HMAC)
  ✓ windows_anti_loop.py        - Module Anti-Loop
  ✓ windows_clipboard.py        - Module Clipboard
  ✓ test_modules.py             - Tests unitaires
"""

# ============================================================================
# ÉTAPE 1: CLONER & INITIALISER
# ============================================================================

"""
1. Cloner ou créer le repo:
   
   git clone https://github.com/DEVELVIS54/Clipboard-LAN.git
   cd Clipboard-LAN

2. Initialiser la structure du projet:
   
   python init_project.py
   
   Cela crée:
   - windows/ avec sous-dossiers (core, network, storage, sync, ui, utils)
   - android/ avec sous-dossiers
   - tests/
   - docs/
   - windows/data/ (pour SQLite et clés)

3. Vérifier la structure:
   
   # Windows
   tree /F /A Clipboard-LAN
   
   # Linux/Mac
   tree Clipboard-LAN -L 3

RÉSULTAT ATTENDU:
  Clipboard-LAN/
    ├── windows/
    │   ├── __init__.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── security.py ✓ (à copier)
    │   │   ├── clipboard.py ✓ (à copier)
    │   │   └── anti_loop.py ✓ (à copier)
    │   ├── network/
    │   ├── storage/
    │   ├── sync/
    │   ├── ui/
    │   ├── utils/
    │   └── data/
    │       └── keys/
    ├── android/
    ├── tests/
    │   ├── __init__.py
    │   └── test_modules.py ✓ (à copier)
    ├── docs/
    ├── config.py ✓
    ├── requirements.txt ✓
    └── README.md ✓
"""

# ============================================================================
# ÉTAPE 2: INSTALLER LES DÉPENDANCES
# ============================================================================

"""
1. Créer un virtualenv (recommandé):
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate

2. Installer requirements.txt:
   
   pip install -r requirements.txt
   
   Cela installe:
   - websockets (WebSocket async)
   - cryptography (RSA, HMAC)
   - zeroconf (mDNS)
   - pyperclip (Clipboard access)
   - pytest (Tests)
   - Et autres dépendances

3. Vérifier l'installation:
   
   python -c "import websockets, cryptography, zeroconf, pyperclip; print('✓ OK')"
   
   RÉSULTAT ATTENDU:
   ✓ OK

4. Vérifier pytest:
   
   pytest --version
   
   RÉSULTAT ATTENDU:
   pytest 7.4.3
"""

# ============================================================================
# ÉTAPE 3: COPIER LES MODULES
# ============================================================================

"""
Copier les fichiers .py fournis dans la structure:

1. Module Security:
   windows_security.py → windows/core/security.py

2. Module Anti-Loop:
   windows_anti_loop.py → windows/core/anti_loop.py

3. Module Clipboard:
   windows_clipboard.py → windows/core/clipboard.py

4. Tests:
   test_modules.py → tests/test_modules.py

APRÈS:
  windows/core/
    ├── security.py ✓
    ├── anti_loop.py ✓
    └── clipboard.py ✓
  
  tests/
    └── test_modules.py ✓
"""

# ============================================================================
# ÉTAPE 4: LANCER LES TESTS
# ============================================================================

"""
1. Lancer tous les tests:
   
   pytest tests/ -v
   
   RÉSULTAT ATTENDU:
   ============================= test session starts ==============================
   collected 50 items
   
   tests/test_modules.py::TestSecurityManager::test_key_generation PASSED  [ 2%]
   tests/test_modules.py::TestSecurityManager::test_public_key_pem_format PASSED  [ 4%]
   ...
   ========================= 50 passed in 3.45s ==========================

2. Lancer un test spécifique:
   
   pytest tests/test_modules.py::TestSecurityManager -v
   
   ou
   
   pytest tests/test_modules.py::TestSecurityManager::test_rsa_encrypt_decrypt -v

3. Avec couverture:
   
   pytest tests/ --cov=windows --cov-report=html
   
   Cela crée un rapport HTML: htmlcov/index.html

4. Logs verbose:
   
   pytest tests/ -v -s
   
   (-s affiche les print() en temps réel)
"""

# ============================================================================
# ÉTAPE 5: TESTER MANUELLEMENT LES MODULES
# ============================================================================

"""
1. Tester Security:
   
   python windows/core/security.py
   
   RÉSULTAT ATTENDU:
   🧪 Tests du module Security
   
   1️⃣  Test RSA Encryption/Decryption
     ✓ Plaintext: Hello, Clipboard LAN!
     ✓ Encrypted: jX8kL9...
     ✓ Decrypted: Hello, Clipboard LAN!
   
   2️⃣  Test RSA Signature/Verification
     ✓ Message: Device authentication
     ✓ Signature: aB3kL9...
     ✓ Verification: True
   
   ... (plus de tests)
   
   ✅ Tous les tests de sécurité passent!

2. Tester Anti-Loop:
   
   python windows/core/anti_loop.py
   
   RÉSULTAT ATTENDU:
   🧪 Tests du module Anti-Loop
   
   1️⃣  Test AntiLoopCache
     ✓ Hash: a1b2c3d4...
     ✓ Deuxième ajout détecté comme boucle
   
   ... (plus de tests)
   
   ✅ Tous les tests anti-loop passent!

3. Tester Clipboard:
   
   python windows/core/clipboard.py
   
   RÉSULTAT ATTENDU:
   🧪 Tests du module Clipboard
   
   1️⃣  Test ClipboardManager
     ✓ Écriture: Test Clipboard LAN
     ✓ Lecture: Test Clipboard LAN
   
   ... (plus de tests)
   
   ✅ Tous les tests clipboard passent!
"""

# ============================================================================
# ÉTAPE 6: VÉRIFIER LA CONFIGURATION
# ============================================================================

"""
1. Vérifier que config.py fonctionne:
   
   python config.py
   
   RÉSULTAT ATTENDU:
   Project root: C:\...\Clipboard-LAN
   Database: C:\...\Clipboard-LAN\windows\data\clipboard_lan.db
   Keys: C:\...\Clipboard-LAN\windows\data\keys
   WebSocket: ws://0.0.0.0:7777
   mDNS Service: _clipboard-lan._tcp.local.
   All directories created ✓

2. Vérifier les clés générées:
   
   ls -la windows/data/keys/
   
   RÉSULTAT ATTENDU:
   rsa_private_key.pem    (2KB)
   rsa_public_key.pem     (400B)
   hmac_secret.key        (32B)
"""

# ============================================================================
# ÉTAPE 7: DIAGNOSTIC DES ERREURS COURANTES
# ============================================================================

"""
ERREUR: ModuleNotFoundError: No module named 'cryptography'
SOLUTION:
  pip install cryptography==42.0.0

ERREUR: pyperclip.PyperclipException: Pyperclip could not find
SOLUTION:
  Windows: Généralement fonctionne
  Linux: sudo apt-get install xclip
  Mac: Généralement fonctionne

ERREUR: OSError: [Errno 48] Address already in use (port 7777)
SOLUTION:
  netstat -ano | findstr :7777  (Windows)
  lsof -i :7777                  (Linux/Mac)
  Ou changer WEBSOCKET_PORT dans config.py

ERREUR: PermissionError: [Errno 13] Permission denied
SOLUTION:
  S'assurer d'avoir les droits en écriture sur windows/data/
  chmod -R 755 windows/data/  (Linux/Mac)

ERREUR: pytest command not found
SOLUTION:
  pip install pytest==7.4.3
  Ou: python -m pytest tests/ -v

ERREUR: RSA key too small
SOLUTION:
  config.py utilise RSA_KEY_SIZE = 2048 (correct)
  Vérifier que security.py n'est pas modifié
"""

# ============================================================================
# ÉTAPE 8: PROCHAINES PHASES
# ============================================================================

"""
✅ PHASE 1 COMPLÈTE: Security + Anti-Loop + Clipboard

PROCHAINES ÉTAPES (dans l'ordre):

□ PHASE 2: Network Module (WebSocket + mDNS)
  - windows/network/websocket_server.py
  - windows/network/mdns_announcer.py
  - windows/network/protocol.py
  - Tests: test_network.py

□ PHASE 3: Storage Module (SQLite)
  - windows/storage/database.py
  - windows/storage/devices.py
  - windows/storage/history.py
  - windows/storage/settings.py
  - Tests: test_storage.py

□ PHASE 4: Sync Manager (Orchestration)
  - windows/sync/sync_manager.py
  - windows/sync/device_manager.py
  - windows/sync/state.py
  - Tests: test_sync.py

□ PHASE 5: UI (Tkinter)
  - windows/ui/main_window.py
  - windows/ui/device_panel.py
  - windows/ui/history_panel.py
  - windows/ui/settings_dialog.py
  - Tests: test_ui.py (intégration)

□ PHASE 6: Main App
  - windows/main.py (entry point)
  - Build EXE avec PyInstaller
  - Tests complets

□ PHASE 7: Android (Flutter)
  - android/lib/main.dart
  - Modules core/network/storage/sync
  - UI Flutter
  - Tests

□ PHASE 8: Tests d'intégration Android ↔ Windows
"""

# ============================================================================
# ÉTAPE 9: STRUCTURE D'UN MODULE NOUVEAU
# ============================================================================

"""
Quand tu créeras un nouveau module, suis ce template:

1. Fichier: windows/<category>/<module>.py

2. Structure du fichier:
   
   \"\"\"
   CLIPBOARD LAN - Module <Name>
   <Description courte>
   
   PHASE <N>: <Category>
   \"\"\"
   
   # Imports
   import ...
   
   # Classe principale
   class <ModuleName>:
       def __init__(self, ...):
           ...
       
       def method1(self):
           ...
       
       def method2(self):
           ...
   
   # Tests locaux
   if __name__ == \"__main__\":
       print(\"🧪 Tests du module <Name>\n\")
       # Tests ici
       print(\"✅ Tous les tests passent!\")

3. Tests: tests/test_<module>.py
   
   import pytest
   
   class Test<ModuleName>:
       def test_method1(self):
           ...

4. Ajouter à config.py si nécessaire

5. Lancer tests:
   
   pytest tests/test_<module>.py -v
"""

# ============================================================================
# RÉSUMÉ CHECKLIST
# ============================================================================

"""
CHECKLIST DE DÉMARRAGE:

□ Python 3.9+ installé
□ Git configuré
□ Repo Clipboard-LAN créé/cloné
□ init_project.py lancé
□ requirements.txt installé
□ Modules (security, anti_loop, clipboard) copiés
□ Tests lancés (pytest)
   □ TestSecurityManager (10 tests)
   □ TestAntiLoopCache (4 tests)
   □ TestLoopDetector (6 tests)
   □ TestClipboardManager (8 tests)
   □ TestClipboardSyncAdapter (5 tests)
   □ TestIntegration (1 test)
   → Total: 34+ tests, tous PASSED
□ Tests manuels lancés
   □ python windows/core/security.py
   □ python windows/core/anti_loop.py
   □ python windows/core/clipboard.py
□ Config vérifiée (python config.py)
□ Clés générées dans windows/data/keys/
□ Dépôt Git initialisé
   git add .
   git commit -m "Initial commit: Phase 1 complete"
   git push

✅ PRÊT POUR PHASE 2 (Network)
"""

# ============================================================================
# COMMANDES RAPIDES
# ============================================================================

"""
# Initialiser projet
python init_project.py

# Installer dépendances
pip install -r requirements.txt

# Lancer tous les tests
pytest tests/ -v

# Lancer tests spécifiques
pytest tests/test_modules.py::TestSecurityManager -v

# Tests avec couverture
pytest tests/ --cov=windows --cov-report=html

# Tester un module seul
python windows/core/security.py
python windows/core/anti_loop.py
python windows/core/clipboard.py

# Vérifier config
python config.py

# Git
git init
git add .
git commit -m "Initial: Phase 1"
git branch develop
git checkout develop
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              CLIPBOARD LAN - GUIDE DE DÉMARRAGE COMPLET                   ║
║                                                                            ║
║  1. Initialiser: python init_project.py                                   ║
║  2. Installer: pip install -r requirements.txt                            ║
║  3. Copier modules: windows/core/{security,anti_loop,clipboard}.py        ║
║  4. Tester: pytest tests/ -v                                              ║
║  5. Valider: python windows/core/*.py                                     ║
║                                                                            ║
║  ✅ PHASE 1 COMPLÈTE: Security + Anti-Loop + Clipboard                   ║
║  → Prêt pour PHASE 2: Network (WebSocket + mDNS)                         ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
