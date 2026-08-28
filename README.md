# Clipboard LAN (ELYON)

**Synchronisation sécurisée du presse-papier entre Android et Windows sur réseau local.**

---

## 🎯 Vision

Donner l'impression que le téléphone et le PC disposent d'un presse-papier commun, sans serveur central, sans compte, sans Internet.

**Principe directeur : CONFIGURER UNE FOIS — UTILISER TOUJOURS**

---

## 📋 Caractéristiques

- ✅ Synchronisation bidirectionnelle Android ↔ Windows
- ✅ Réseau local (LAN) - pas d'Internet requis
- ✅ Sécurisée : WebSocket chiffré + authentification RSA/HMAC
- ✅ Découverte automatique via mDNS
- ✅ Association par QR code
- ✅ Reconnexion automatique
- ✅ Historique local optionnel
- ✅ Démarrage automatique Windows
- ✅ Gestion multi-appareils
- ✅ Anti-boucles de synchronisation

---

## 🛠 Stack technologique

| Plateforme | Stack | Port |
|-----------|-------|------|
| **Windows** | Python 3.9+ / Tkinter | 7777 |
| **Android** | Flutter / Dart | Client |
| **Réseau** | WebSocket + mDNS | LAN |
| **Base** | SQLite | Local |
| **Sécurité** | RSA-2048 + HMAC-SHA256 | TLS futur |

---

## 📁 Structure du projet

```
Clipboard-LAN/
├── windows/               # Python/Tkinter (serveur + UI)
├── android/              # Flutter/Dart (client mobile)
├── tests/                # Tests unitaires & intégration
├── docs/                 # Documentation complète
├── shared/               # Specs et test vectors
└── config.py             # Configuration centralisée
```

Voir `docs/ARCHITECTURE.md` pour le détail complet.

---

## 🚀 Démarrage rapide

### Prérequis

```bash
# Windows
- Python 3.9+
- Git
- Flutter SDK (pour Android)

# Android
- Flutter SDK
- Android SDK (API 21+)
```

### Installation Windows

```bash
# 1. Cloner le repo
git clone https://github.com/DEVELVIS54/Clipboard-LAN.git
cd Clipboard-LAN

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'app
python windows/main.py

# 4. Ou lancer les tests
pytest tests/ -v
```

### Installation Android

```bash
# 1. Aller au dossier Android
cd android

# 2. Installer les dépendances
flutter pub get

# 3. Lancer sur device/emulateur
flutter run
```

---

## 🧪 Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_security.py -v      # Crypto
pytest tests/test_clipboard.py -v     # Clipboard + anti-loop
pytest tests/test_network.py -v       # WebSocket + mDNS
pytest tests/test_integration.py -v   # Bout-en-bout

# Avec couverture
pytest tests/ --cov=windows --cov-report=html
```

---

## 📚 Documentation

- **[Cahier des charges v2.0](docs/CAHIER_DES_CHARGES_v2.0.md)** — Spécifications complètes
- **[Architecture](docs/ARCHITECTURE.md)** — Vue système et composants
- **[Protocole](docs/PROTOCOL_SPEC.md)** — Spécification WebSocket
- **[Sécurité](docs/SECURITY.md)** — Authentification, chiffrement, révocation
- **[API Messages](docs/API_MESSAGES.md)** — Détail des messages protocole
- **[Plan de tests](docs/TESTING_PLAN.md)** — Stratégie et couverture

---

## 🔒 Sécurité

- **Pas de confiance implicite du réseau** : même réseau ≠ confiance
- **Authentification** : RSA-2048 + HMAC-SHA256
- **Chiffrement** : WebSocket + TLS (futur)
- **Révocation** : capacité à révoquer des appareils
- **Privacy by Design** : aucun serveur central, aucun cloud, aucune collecte distante

Voir `docs/SECURITY.md` pour les détails.

---

## 📈 Phases de développement

| Phase | Composant | État |
|-------|-----------|------|
| 1 | Security (RSA, HMAC) | 🚀 À faire |
| 2 | Clipboard + anti-loop | 🚀 À faire |
| 3 | Network (WebSocket, mDNS) | 🚀 À faire |
| 4 | Storage (SQLite) | 🚀 À faire |
| 5 | Sync Manager | 🚀 À faire |
| 6 | UI Tkinter (Windows) | 🚀 À faire |
| 7 | Tests intégration | 🚀 À faire |
| 8 | Android (Flutter) | 🚀 À faire |

---

## 🎯 Critères de réussite MVP

✅ Association Android/Windows  
✅ Refus des appareils inconnus  
✅ Android → Windows  
✅ Windows → Android  
✅ Fonctionnement sans Internet  
✅ Reconnexion automatique  
✅ Démarrage automatique Windows  
✅ Communications sécurisées  
✅ Anti-boucles  
✅ Performance < 100ms  
✅ Historique optionnel  

---

## 🔮 Évolutions futures

- **V2** : images, petits fichiers, recherche historique
- **V3** : plusieurs PC/téléphones, profils, filtrage intelligent
- **V4** : Linux, macOS, iOS

---

## 👤 Auteur

**Elvis (FasoDev)**  
- GitHub: https://github.com/DEVELVIS54
- Portfolio: https://develvis54.github.io/Fasodev/
- Contact: develvis76@gmail.com

---

## 📄 Licence

À définir (MIT, Apache 2.0, etc.)

---

## 📞 Support & Contribution

Pour toute question ou contribution, ouvrir une **issue** ou **PR** sur GitHub.

---

**Code de projet : ELYON**  
**Version : 1.0.0-alpha**  
**Statut : En développement actif**
