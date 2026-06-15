"""
KITT Theme - Colores, fuentes y constantes del estilo Knight Rider
"""
from kivy.utils import get_color_from_hex

# === PALETA KITT ===
COLORS = {
    'bg': '#050508',
    'bg_dash': '#080810',
    'surface': '#0a0a14',
    'surface2': '#121222',
    'surface3': '#1a1a30',
    'panel': '#0e0e1a',
    'border': '#1a1a2e',
    
    'kitt_red': '#ff1a1a',
    'kitt_bright': '#ff4444',
    'kitt_glow': '#ff2222',
    'kitt_dim': '#330000',
    'kitt_off': '#1a0000',
    'kitt_pulse': '#ff6666',
    
    'amber': '#ffaa00',
    'amber_dim': '#332200',
    'green': '#00ff88',
    'green_dim': '#003322',
    'blue': '#4488ff',
    'blue_dim': '#001133',
    
    'text': '#e0e0e0',
    'text_bright': '#ffffff',
    'text_dim': '#555577',
    'text_dimmer': '#333355',
    'text_red': '#ff5555',
    
    'user_msg': '#1a0808',
    'user_msg_border': '#2a1010',
    'assistant_msg': '#0a0a18',
    'assistant_msg_border': '#1a1a2e',
    
    'nav_inactive': '#222244',
    'nav_active': '#ff1a1a',
    'nav_bg': '#06060e',
}

# Convertir a tuplas rgba para Kivy
def c(name, alpha=1.0):
    """Devuelve un color en formato rgba para Kivy."""
    hex_color = COLORS.get(name, '#ffffff')
    r, g, b = get_color_from_hex(hex_color)[:3]
    return (r, g, b, alpha)

# ============================================================
#  DIMENSIONES
# ============================================================
SCANNER_HEIGHT = 110
NAV_HEIGHT = 54
STATUS_BAR_HEIGHT = 24
INPUT_HEIGHT = 50

NUM_LEDS = 24

# ============================================================
#  ESTADOS DEL SCANNER
# ============================================================
SCAN_IDLE = "idle"       # Slow scan
SCAN_LISTEN = "listen"    # Fast scan with pulse
SCAN_THINK = "think"      # Random flicker
SCAN_SPEAK = "speak"      # Wave from center
SCAN_ALERT = "alert"      # Fast flashing (error/attention)
