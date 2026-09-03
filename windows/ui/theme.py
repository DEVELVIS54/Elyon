"""
CLIPBOARD LAN - Theme
Système de design: panneau de contrôle réseau/sécurité, graphite + signal cyan

CHEMIN: windows/ui/theme.py
"""

# ============================================================================
# COULEURS
# ============================================================================

COLORS = {
    # Fond
    "background": "#0F1115",
    "surface": "#17191C",
    "surface_raised": "#1D2024",
    "surface_hover": "#22252A",

    # Rail / navigation (intégré au fond, pas un îlot séparé)
    "rail": "#0F1115",
    "rail_active": "#1D2024",
    "rail_icon": "#5C6068",
    "rail_icon_active": "#E7E8EA",

    # Texte
    "text_primary": "#E7E8EA",
    "text_secondary": "#8A8F98",
    "text_dim": "#5C6068",
    "text_on_accent": "#0F1115",

    # Accent unique — signal
    "accent": "#4CE0C4",
    "accent_dim": "#2E7A6A",

    # États (utilisés avec parcimonie, jamais comme fond de card)
    "success": "#4CE0C4",
    "warning": "#E8A33D",
    "error": "#E8555F",
    "offline": "#5C6068",

    # Bordures
    "border": "#2A2D33",
    "border_strong": "#3A3E46",
}


# ============================================================================
# POLICES — Segoe UI pour l'interface, Consolas pour toute donnée technique
# (device IDs, tailles, ports, horodatages) : la distinction typographique
# EST l'information, pas une décoration.
# ============================================================================

FONTS = {
    "family": "Segoe UI",
    "family_mono": "Consolas",

    "size_xs": 11,
    "size_sm": 12,
    "size_base": 13,
    "size_lg": 16,
    "size_xl": 20,
    "size_2xl": 28,

    "weight_normal": "normal",
    "weight_bold": "bold",
}


# ============================================================================
# ESPACEMENT / RAYONS — coins presque droits (4-8px), pas le "tout arrondi"
# ============================================================================

SPACING = {
    "xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32, "2xl": 48,
}

RADIUS = {
    "sm": 4, "md": 6, "lg": 8, "full": 999,
}

DIMENSIONS = {
    "rail_width": 64,
    "window_width": 1080,
    "window_height": 680,
}


# ============================================================================
# STATUT — pastille pleine + libellé mono, jamais d'emoji décoratif
# ============================================================================

STATUS_SYMBOLS = {
    "connected": "●",
    "disconnected": "○",
    "pending": "◐",
}

NAV_LABELS = {
    "dashboard": "SYNC",
    "devices": "APPAREILS",
    "history": "HISTORIQUE",
    "settings": "CONFIG",
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
    print("✅ Theme v2 ready — graphite/cyan technical panel")