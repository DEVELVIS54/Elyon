#!/usr/bin/env python3
"""
CLIPBOARD LAN - Initialisation du projet
Crée la structure complète et valide la configuration.
"""

import os
import sys
from pathlib import Path

# ============================================================================
# Directories à créer
# ============================================================================

DIRECTORIES = [
    # Windows
    "windows",
    "windows/core",
    "windows/network",
    "windows/storage",
    "windows/sync",
    "windows/ui",
    "windows/utils",
    "windows/data",
    "windows/data/keys",
    
    # Android
    "android",
    "android/lib",
    "android/lib/core",
    "android/lib/network",
    "android/lib/storage",
    "android/lib/sync",
    "android/lib/ui",
    "android/lib/ui/screens",
    "android/lib/ui/widgets",
    "android/lib/models",
    
    # Tests & Docs
    "tests",
    "docs",
    "shared",
    "scripts",
]

# ============================================================================
# Fichiers __init__.py à créer
# ============================================================================

PYTHON_PACKAGES = [
    "windows/__init__.py",
    "windows/core/__init__.py",
    "windows/network/__init__.py",
    "windows/storage/__init__.py",
    "windows/sync/__init__.py",
    "windows/ui/__init__.py",
    "windows/utils/__init__.py",
    "tests/__init__.py",
]

# ============================================================================
# Fonction principale
# ============================================================================

def init_project():
    """Initialise la structure complète du projet."""
    
    print("=" * 70)
    print("CLIPBOARD LAN - INITIALISATION DU PROJET".center(70))
    print("=" * 70)
    print()
    
    # Créer les répertoires
    print("📁 Création des répertoires...")
    for directory in DIRECTORIES:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print()
    
    # Créer les fichiers __init__.py
    print("📝 Création des packages Python...")
    for init_file in PYTHON_PACKAGES:
        path = Path(init_file)
        path.touch(exist_ok=True)
        print(f"  ✓ {init_file}")
    
    print()
    
    # Vérifier les fichiers de config
    print("⚙️  Vérification des fichiers de configuration...")
    required_files = [
        "config.py",
        "requirements.txt",
        ".gitignore",
        "README.md",
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ⚠️  {file} - À créer manuellement")
    
    print()
    
    # Initier un dépôt Git
    if not Path(".git").exists():
        print("🔧 Initialisation du dépôt Git...")
        os.system("git init > /dev/null 2>&1")
        os.system("git config user.email 'dev@fasodev.local' > /dev/null 2>&1")
        os.system("git config user.name 'Elvis FasoDev' > /dev/null 2>&1")
        print("  ✓ .git créé")
    else:
        print("  ℹ️  Dépôt Git existant")
    
    print()
    
    # Résumé
    print("=" * 70)
    print("✅ INITIALISATION COMPLÈTE".center(70))
    print("=" * 70)
    print()
    print("Prochaines étapes:")
    print("  1. pip install -r requirements.txt")
    print("  2. python windows/main.py  (à implémenter)")
    print("  3. pytest tests/  (après implémentation)")
    print()
    print("Documentation:")
    print("  • README.md — Vue d'ensemble")
    print("  • docs/ — Documentation complète")
    print("  • config.py — Constantes & paramètres")
    print()


if __name__ == "__main__":
    try:
        init_project()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
