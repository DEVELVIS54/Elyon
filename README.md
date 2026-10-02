# ELYON (EasyCV) — Générateur de CV Professionnel par IA

Plateforme SaaS Django dédiée à la création et à la génération de **CV professionnels de haute qualité**, assistée par l'intelligence artificielle (**Groq LLM & Vision**) et propulsée par un moteur de rendu vectoriel (**ReportLab**).

---

## 🌟 Fonctionnalités Principales

- **Authentification & Onboarding** :
  - Inscription, connexion, déconnexion avec création automatique du profil.
  - Parcours d'onboarding fluide pour guider les nouveaux utilisateurs.

- **Gestion Complète du Profil Candidat** :
  - Identité : nom, profession, coordonnées, photo, biographie, statut de disponibilité.
  - Réseaux professionnels & liens : GitHub, LinkedIn, site personnel, Twitter/X, etc.
  - Compétences techniques avec notation de niveau.
  - Expériences professionnelles (intitulé, entreprise, dates, description).
  - Formations et diplômes (établissement, diplôme, période).

- **Professional Score (/100)** :
  - Score dynamique calculé en temps réel selon la complétude du CV.
  - Conseils personnalisés pour maximiser l'impact de la candidature.

- **Catalogue de Thèmes & Analyse Vision par IA** :
  - Catalogue de modèles visuels uploadés via l'admin Django.
  - Analyse d'image automatisée par **Groq Vision** (`GROQ_VISION_MODEL`) pour extraire une fiche de style structurée :
    - Palette de couleurs dominante et secondaire
    - Style typographique (moderne, classique, technique, audacieux)
    - Archétype de mise en page (`single-column`, `sidebar`, `header-band`)
    - Rythme et espacement vertical
  - Sélection ou réinitialisation de thème en un clic depuis le dashboard.

- **Moteur de Génération PDF (ReportLab)** :
  - Génération vectorielle nette et ultra-rapide au format A4.
  - 3 archétypes de mise en page intégrés :
    1. **Single-Column** : classique, élégant et épuré.
    2. **Sidebar** : colonne latérale colorée avec mise en valeur des compétences et contacts.
    3. **Header-Band** : bannière supérieure avec coordonnées intégrées.
  - Prévisualisation inline dans le navigateur ou téléchargement direct en pièce jointe.

- **Assistant IA (Groq)** :
  - Génération et reformulation de biographie professionnelle selon le ton souhaité.
  - Suggestions intelligentes de compétences selon le métier.
  - Audit et analyse critique du profil avec recommandations d'amélioration.
  - Assistant conversationnel interactif directement accessible sur le tableau de bord.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.10+, Django 6.1
- **Base de données** : SQLite (développement) — compatible PostgreSQL (production)
- **Génération PDF** : ReportLab 4.0+
- **Traitement d'images** : Pillow 10.0+
- **Intelligence Artificielle** : API Groq (`openai/gpt-oss-120b` pour le texte, `qwen/qwen3.6-27b` pour la vision)
- **Frontend** : Django Templates, Bootstrap 5 (CDN), CSS custom (`static/css/elyon.css`)
- **Typographie** : Anton, Inter, JetBrains Mono

---

## 📂 Architecture du Projet

```text
ELYON_CV_Django/
├── config/           # Configuration globale Django, settings, routage principal
├── accounts/         # Authentification (inscription, connexion, déconnexion)
├── profiles/         # Profil utilisateur, compétences, expériences, formations, dashboard & score
├── cvgen/            # Thèmes de CV, moteur de rendu ReportLab, export & preview PDF
├── ai/               # Services Groq (prompts, génération textuelle, analyse vision de thèmes)
├── templates/        # Templates HTML Jinja/Django
├── static/           # Feuilles de style CSS, scripts et assets graphiques
├── media/            # Stockage des uploads (photos de profil, images de thèmes, PDF générés)
└── manage.py         # Point d'entrée des commandes Django
```

---

## 🚀 Installation & Démarrage

### 1. Cloner le dépôt et créer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows (PowerShell) :
venv\Scripts\Activate.ps1
# Sur Linux / macOS :
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Copiez le fichier `.env.example` en `.env` :

```bash
cp .env.example .env
```

Puis configurez votre clé API Groq dans `.env` :
```env
SECRET_KEY=votre-cle-secrete-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=votre_cle_api_groq_ici
GROQ_MODEL=openai/gpt-oss-120b
GROQ_VISION_MODEL=qwen/qwen3.6-27b
```

### 4. Appliquer les migrations et créer un compte administrateur

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Lancer les tests automatisés

```bash
python manage.py test
```

### 6. Démarrer le serveur de développement

```bash
python manage.py runserver
```

Rendez-vous sur [http://127.0.0.1:8000/](http://127.0.0.1:8000/) pour utiliser l'application, ou sur [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) pour accéder à l'interface d'administration et gérer les thèmes de CV.
