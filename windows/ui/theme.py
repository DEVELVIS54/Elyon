"""
CLIPBOARD LAN - Theme
Couleurs, polices et styles pour l'interface

CHEMIN: windows/ui/theme.py
"""

# ============================================================================
# COULEURS
# ============================================================================

COLORS = {
    # Fond
    "background": "#E8ECF1",
    "background_light": "#F5F7FA",
    
    # Sidebar
    "sidebar": "#1A2332",
    "sidebar_hover": "#242F42",
    "sidebar_active": "#2D3A52",
    "sidebar_icon": "#8B95A5",
    "sidebar_icon_active": "#FFFFFF",
    
    # Cards
    "card": "#FFFFFF",
    "card_hover": "#F5F7FA",
    "card_border": "#E1E5EB",
    
    # Texte
    "text_primary": "#1A2332",
    "text_secondary": "#8B95A5",
    "text_light": "#B4BCC8",
    "text_white": "#FFFFFF",
    
    # Accents
    "accent": "#1A2332",
    "accent_blue": "#3B82F6",
    "accent_green": "#22C55E",
    "accent_red": "#EF4444",
    "accent_orange": "#F59E0B",
    
    # États
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
    
    # Bordures
    "border": "#E1E5EB",
    "border_light": "#F0F2F5",
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
    "size_lg": 15,
    "size_xl": 18,
    "size_2xl": 24,
    "size_3xl": 32,
    
    "weight_normal": "normal",
    "weight_bold": "bold",
}


# ============================================================================
# ESPACEMENT
# ============================================================================

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
}


# ============================================================================
# RAYONS DE COINS
# ============================================================================

RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 16,
    "xl": 20,
    "full": 999,
}


# ============================================================================
# DIMENSIONS
# ============================================================================

DIMENSIONS = {
    "sidebar_width": 80,
    "window_width": 1000,
    "window_height": 650,
    "card_min_height": 100,
    "icon_size": 24,
}


# ============================================================================
# ICÔNES (emoji utilisés comme icônes simples)
# ============================================================================

ICONS = {
    "dashboard": "📊",
    "devices": "📱",
    "history": "📝",
    "settings": "⚙️",
    "notifications": "🔔",
    "sync": "🔄",
    "connected": "🟢",
    "disconnected": "🔴",
    "trusted": "✅",
    "pending": "⏳",
    "windows": "💻",
    "android": "📱",
    "success": "✅",
    "error": "❌",
    "clipboard": "📋",
}


# ============================================================================
# HELPERS
# ============================================================================

def get_status_color(status: str) -> str:
    """Retourne la couleur associée à un statut."""
    status_map = {
        "connected": COLORS["success"],
        "disconnected": COLORS["error"],
        "pending": COLORS["warning"],
        "trusted": COLORS["success"],
        "untrusted": COLORS["warning"],
        "success": COLORS["success"],
        "failed": COLORS["error"],
    }
    return status_map.get(status.lower(), COLORS["text_secondary"])


def get_font(size_key: str = "base", weight: str = "normal") -> tuple:
    """Retourne un tuple de police pour Tkinter/CustomTkinter."""
    size = FONTS.get(f"size_{size_key}", FONTS["size_base"])
    return (FONTS["family"], size, weight)


if __name__ == "__main__":
    print("✅ Theme module ready")
    print(f"Colors: {len(COLORS)} defined")
    print(f"Fonts: {FONTS['family']}")