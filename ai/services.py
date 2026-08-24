"""
Service d'intégration Groq pour LinkBio/ELYON.

Architecture :
    Vue Django -> ai.services.call_groq() -> API Groq -> texte généré

La clé API est lue depuis settings.GROQ_API_KEY (chargée depuis .env).
Ne jamais committer de clé en dur dans ce fichier.
"""

import requests
from django.conf import settings

from .prompts import SYSTEM_PROMPT

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class AIServiceError(Exception):
    """Levée quand l'appel à Groq échoue ou que la clé API est absente."""
    pass


def call_groq(user_prompt, max_tokens=300, temperature=0.7):
    """
    Envoie un prompt à l'API Groq (format compatible OpenAI chat completions)
    et retourne le texte de la réponse.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise AIServiceError(
            "GROQ_API_KEY n'est pas configurée. Ajoute-la dans ton fichier .env."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_completion_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AIServiceError(f"Erreur lors de l'appel à Groq : {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise AIServiceError(f"Réponse Groq inattendue : {data}") from exc


# --- Fonctions métier de haut niveau -----------------------------------

def generate_bio(profession, skills, experience_years, tone="professionnel"):
    from .prompts import bio_generate_prompt
    return call_groq(bio_generate_prompt(profession, skills, experience_years, tone))


def improve_bio(raw_text):
    from .prompts import bio_improve_prompt
    return call_groq(bio_improve_prompt(raw_text))


def suggest_skills(profession, existing_skills):
    from .prompts import skill_suggestions_prompt
    result = call_groq(skill_suggestions_prompt(profession, existing_skills))
    return [s.strip() for s in result.split(',') if s.strip()]


def analyze_profile(profile_summary):
    from .prompts import profile_analysis_prompt
    return call_groq(profile_analysis_prompt(profile_summary))


def ask_assistant(user_question, context_summary=""):
    from .prompts import assistant_prompt
    return call_groq(assistant_prompt(user_question, context_summary), max_tokens=400)


# --- Analyse vision (thèmes de CV) --------------------------------------

VALID_TYPOGRAPHY_MOODS = {"modern", "classic", "technical", "bold"}
VALID_LAYOUT_ARCHETYPES = {"single-column", "sidebar", "header-band"}
VALID_SPACINGS = {"compact", "comfortable", "spacious"}

DEFAULT_DESIGN_SPEC = {
    "palette": ["#E8231A", "#141414"],
    "typography_mood": "modern",
    "layout_archetype": "single-column",
    "spacing": "comfortable",
}


def _sanitize_design_spec(raw):
    """Valide et nettoie la fiche de style renvoyée par l'IA. Toute valeur
    absente ou invalide retombe sur la valeur par défaut correspondante,
    pour que le moteur de rendu du CV reçoive toujours des données sûres."""
    import re

    spec = dict(DEFAULT_DESIGN_SPEC)

    palette = raw.get("palette")
    if isinstance(palette, list):
        hex_colors = [c for c in palette if isinstance(c, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c)]
        if hex_colors:
            spec["palette"] = hex_colors[:3]

    mood = raw.get("typography_mood")
    if mood in VALID_TYPOGRAPHY_MOODS:
        spec["typography_mood"] = mood

    archetype = raw.get("layout_archetype")
    if archetype in VALID_LAYOUT_ARCHETYPES:
        spec["layout_archetype"] = archetype

    spacing = raw.get("spacing")
    if spacing in VALID_SPACINGS:
        spec["spacing"] = spacing

    return spec


def analyze_theme_image(image_bytes, content_type="image/jpeg"):
    """Envoie l'image à l'IA vision Groq et retourne une fiche de style
    JSON validée (palette, typographie, mise en page, espacement).
    Lève AIServiceError en cas d'échec (clé API absente, erreur réseau,
    réponse invalide)."""
    import base64
    import json

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise AIServiceError(
            "GROQ_API_KEY n'est pas configurée. Ajoute-la dans ton fichier .env."
        )

    from .prompts import theme_vision_prompt

    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": theme_vision_prompt()},
                    {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{b64_image}"}},
                ],
            }
        ],
        "response_format": {"type": "json_object"},
        "reasoning_effort": "none",
        "max_completion_tokens": 600,
        "temperature": 0.3,
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            detail = f" — réponse Groq : {exc.response.text}"
        raise AIServiceError(f"Erreur lors de l'appel vision à Groq : {exc}{detail}") from exc

    data = response.json()
    try:
        raw_content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise AIServiceError(f"Réponse vision Groq inattendue : {data}") from exc

    if not raw_content or not raw_content.strip():
        raise AIServiceError(
            "L'IA a renvoyé une réponse vide pour cette image. "
            "Réessaie, ou choisis une image différente."
        )

    try:
        raw_spec = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise AIServiceError(f"L'IA n'a pas renvoyé un JSON valide : {raw_content}") from exc

    return _sanitize_design_spec(raw_spec)