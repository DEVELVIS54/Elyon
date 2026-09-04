"""
CLIPBOARD LAN - Theme
Système de design clair inspiré du dashboard de référence :
fond bleu-gris pâle, cards blanches, rail d'icônes clair avec
un carré arrondi bleu marine pour l'icône active.

CHEMIN: windows/ui/theme.py
"""

# ============================================================================
# COULEURS
# ============================================================================

COLORS = {
    # Fond général
    "background": "#EDF1F6",
    "background_alt": "#E4E9F0",

    # Rail de navigation — même ton que le fond, pas un îlot séparé
    "rail": "#EDF1F6",
    "rail_icon_bg": "#FFFFFF",
    "rail_icon_bg_hover": "#F5F7FA",
    "rail_icon": "#8C93A3",
    "rail_active_bg": "#151B2C",
    "rail_active_icon": "#FFFFFF",

    # Cards
    "card": "#FFFFFF",
    "card_hover": "#F7F9FB",
    "card_border": "#E3E7ED",

    # Texte
    "text_primary": "#1B2233",
    "text_secondary": "#8C93A3",
    "text_light": "#B7BDC9",
    "text_on_dark": "#FFFFFF",

    # Accent — même bleu marine que l'icône active, utilisé avec parcimonie
    "accent": "#151B2C",
    "accent_soft": "#EEF0F4",

    # États
    "success": "#2FBE8F",
    "warning": "#E8A33D",
    "error": "#E5555F",
    "offline": "#B7BDC9",

    # Bordures
    "border": "#E3E7ED",
    "border_strong": "#D3D8E0",
}


# ============================================================================
# POLICES
# ============================================================================

FONTS = {
    "family": "Segoe UI",
    "family_mono": "Consolas",

    "size_xs": 11,
    "size_sm": 12,
    "size_base": 13,
    "size_lg": 16,
    "size_xl": 20,
    "size_2xl": 26,

    "weight_normal": "normal",
    "weight_bold": "bold",
}


# ============================================================================
# ESPACEMENT / RAYONS — coins bien arrondis, cohérent avec la référence
# ============================================================================

SPACING = {
    "xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32, "2xl": 48,
}

RADIUS = {
    "sm": 8, "md": 12, "lg": 18, "xl": 22, "full": 999,
}

DIMENSIONS = {
    "rail_width": 76,
    "window_width": 1080,
    "window_height": 680,
}


NAV_LABELS = {
    "dashboard": "Tableau de bord",
    "devices": "Appareils",
    "history": "Historique",
    "settings": "Paramètres",
}


def get_status_color(status: str) -> str:
    """Retourne la couleur associée à un statut."""
    status_map = {
        "connected": COLORS["success"],
        "disconnected": COLORS["offline"],
        "pending": COLORS["warning"],
        "trusted": COLORS["success"],
        "untrusted": COLORS["warning"],
        "success": COLORS["success"],
        "failed": COLORS["error"],
    }
    return status_map.get(status.lower(), COLORS["text_secondary"])


def font(size_key: str = "base", weight: str = "normal", mono: bool = False) -> tuple:
    """Retourne un tuple de police pour CustomTkinter."""
    family = FONTS["family_mono"] if mono else FONTS["family"]
    size = FONTS.get(f"size_{size_key}", FONTS["size_base"])
    return (family, size, weight)


if __name__ == "__main__":
    print("✅ Theme v3 ready — light dashboard style")