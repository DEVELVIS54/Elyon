"""
CLIPBOARD LAN - Configuration globale
Centralise tous les paramètres, constantes et chemins.
"""

import os
from pathlib import Path

# ============================================================================
# RÉPERTOIRES & CHEMINS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.absolute()
WINDOWS_DIR = PROJECT_ROOT / "windows"
ANDROID_DIR = PROJECT_ROOT / "android"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"
SHARED_DIR = PROJECT_ROOT / "shared"

# Base de données et stockage local
DATA_DIR = WINDOWS_DIR / "data"
DB_PATH = DATA_DIR / "clipboard_lan.db"
KEYS_DIR = DATA_DIR / "keys"

# Créer les dossiers s'ils n'existent pas
DATA_DIR.mkdir(parents=True, exist_ok=True)
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# RÉSEAU & COMMUNICATION
# ============================================================================

# WebSocket
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 7777
WEBSOCKET_URI = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"

# mDNS
MDNS_SERVICE_TYPE = "_clipboard-lan._tcp.local."
MDNS_SERVICE_NAME_TEMPLATE = "ClipboardLAN-{device_id}"
MDNS_TIMEOUT = 5  # secondes

# Réseau
NETWORK_TIMEOUT = 10  # secondes
CONNECTION_RETRY_INTERVAL = 5  # secondes
CONNECTION_MAX_RETRIES = 5

# ============================================================================
# SÉCURITÉ & CRYPTOGRAPHIE
# ============================================================================

# RSA
RSA_KEY_SIZE = 2048
RSA_KEY_FILE = KEYS_DIR / "rsa_private_key.pem"
RSA_PUBLIC_KEY_FILE = KEYS_DIR / "rsa_public_key.pem"

# HMAC
HMAC_ALGORITHM = "SHA256"
HMAC_SECRET_FILE = KEYS_DIR / "hmac_secret.key"

# TLS (futures versions)
TLS_CERT_FILE = KEYS_DIR / "device.crt"
TLS_KEY_FILE = KEYS_DIR / "device.key"

# Identité de l'appareil
DEVICE_ID_FILE = DATA_DIR / "device_id.txt"

# ============================================================================
# PRESSE-PAPIER
# ============================================================================

# Moniteur clipboard
CLIPBOARD_POLL_INTERVAL = 0.5  # secondes
CLIPBOARD_MAX_SIZE = 1_000_000  # 1 MB

# Anti-boucle
ANTI_LOOP_CACHE_SIZE = 100
ANTI_LOOP_TIMEOUT = 60  # Vérifier la boucle pendant 60 secondes

# ============================================================================
# BASE DE DONNÉES
# ============================================================================

# SQLite
DATABASE_PRAGMA = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "cache_size": -64_000,  # 64 MB
    "foreign_keys": True,
}

# Historique
HISTORY_RETENTION = 1000  # Nombre max d'entrées
HISTORY_RETENTION_DAYS = 30  # Jours de conservation

# ============================================================================
# PROTOCOLE
# ============================================================================

# Types de messages
MESSAGE_TYPES = {
    "HELLO": 1,
    "DISCOVER": 2,
    "PAIR": 3,
    "AUTH": 4,
    "SYNC": 5,
    "ACK": 6,
    "PING": 7,
    "PONG": 8,
    "DISCONNECT": 9,
    "ERROR": 10,
}

# Types de contenu
CONTENT_TYPES = {
    "text": "text/plain",
    "html": "text/html",
    "url": "text/uri-list",
    "image": "image/png",  # future
}

# Timeout protocole
PROTOCOL_TIMEOUT = 30  # secondes
MESSAGE_ACK_TIMEOUT = 5  # secondes

# ============================================================================
# HISTORIQUE CLIPBOARD
# ============================================================================

HISTORY_ENABLED = True
HISTORY_MAX_ITEMS = 50
HISTORY_RETENTION_DAYS = 30

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = DATA_DIR / "clipboard_lan.log"
LOG_MAX_SIZE = 10_000_000  # 10 MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# UI (TKINTER)
# ============================================================================

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
WINDOW_TITLE = "Clipboard LAN"
WINDOW_ICON = WINDOWS_DIR / "ui" / "assets" / "icon.ico"  # TODO

# ============================================================================
# CONTRAINTES TECHNIQUES
# ============================================================================

# Performance
PERFORMANCE_TARGET_MS = 100  # ms pour sync texte
HEARTBEAT_INTERVAL = 30  # secondes (PING/PONG)

# Android
ANDROID_MIN_API = 21
ANDROID_TARGET_API = 34

# Windows
WINDOWS_MIN_VERSION = "10"

# ============================================================================
# MODES & FEATURES
# ============================================================================

# Mode de destination
DESTINATION_MODES = ["automatic", "targeted"]  # auto ou select device

# Contrôle de fonctionnalités
FEATURES = {
    "history": True,
    "auto_reconnect": True,
    "device_discovery": True,
    "clipboard_monitoring": True,
    "background_service": True,  # Windows seulement
}

# ============================================================================
# VALIDATION & CONSTRAINTS
# ============================================================================

# Noms appareils
DEVICE_NAME_MIN_LENGTH = 1
DEVICE_NAME_MAX_LENGTH = 50

# Message ID
MESSAGE_ID_LENGTH = 32  # UUID hex

# ============================================================================
# VERSION & BUILD
# ============================================================================

APP_VERSION = "1.0.0-alpha"
APP_NAME = "Clipboard LAN"
APP_CODENAME = "ELYON"

# ============================================================================
# DÉVELOPPEMENT
# ============================================================================

DEBUG = False
VERBOSE = False

# Test fixtures
TEST_VECTORS_FILE = SHARED_DIR / "test_vectors.json"
PROTOCOL_SPEC_FILE = SHARED_DIR / "protocol_spec.json"

# ============================================================================
# HELPER: Print config
# ============================================================================

if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Database: {DB_PATH}")
    print(f"Keys: {KEYS_DIR}")
    print(f"WebSocket: {WEBSOCKET_URI}")
    print(f"mDNS Service: {MDNS_SERVICE_TYPE}")
    print(f"All directories created ✓")
