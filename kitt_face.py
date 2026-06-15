"""
KITT Face - El scanner frontal de KITT con LEDs animados
"""
import math
import random as _random
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, PushMatrix, PopMatrix, Translate, Scale
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.animation import Animation

from kitt_theme import *

class KittFace(Widget):
    """La cara frontal de KITT - scanner de 24 LEDs con múltiples modos."""
    
    state = StringProperty(SCAN_IDLE)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(SCANNER_HEIGHT)
        
        # Scanner state
        self.scan_pos = 0.0
        self.direction = 1
        self.speed = 0.012
        self.pulse = 0.0
        self.wave_offset = 0.0
        self.alert_flash = 0.0
        self.num_leds = NUM_LEDS
        self.led_brightness = [0.02] * self.num_leds
        self.glow_intensity = 0.0
        
        # Timer
        Clock.schedule_interval(self.update, 1/60.0)
        
        # Bind redraw on size change
        self.bind(pos=self._redraw, size=self._redraw)
    
    def _redraw(self, *args):
        """Fuerza redibujado cuando cambia tamaño/posición."""
        Clock.schedule_once(lambda dt: self.canvas.ask_update(), 0)
    
    def set_state(self, new_state):
        """Cambia el estado del scanner."""
        self.state = new_state
    
    def update(self, dt):
        """Actualiza la animación cada frame."""
        w = self.width
        now = Clock.get_time()
        
        # Velocidad según estado
        if self.state == SCAN_IDLE:
            self.speed = 0.015
        elif self.state == SCAN_LISTEN:
            self.speed = 0.04
        elif self.state == SCAN_THINK:
            self.speed = 0.0
        elif self.state == SCAN_SPEAK:
            self.speed = 0.0
            self.wave_offset += 0.1
        elif self.state == SCAN_ALERT:
            self.speed = 0.0
            self.alert_flash += 0.15
        
        # Movimiento del scan
        if self.state not in (SCAN_THINK, SCAN_SPEAK, SCAN_ALERT):
            self.scan_pos += self.direction * self.speed
            if self.scan_pos > 0.92:
                self.direction = -1
            elif self.scan_pos < 0.08:
                self.direction = 1
        
        # Pulso general (más rápido en listen)
        pulse_speed = 5 if self.state == SCAN_LISTEN else 2.5
        self.pulse = 0.5 + 0.5 * math.sin(now * pulse_speed)
        
        # Brillo ambiental
        self.glow_intensity = sum(self.led_brightness) / len(self.led_brightness)
        
        # Calcular LEDs
        self._calc_leds()
        self.canvas.ask_update()
    
    def _calc_leds(self):
        """Calcula el brillo de cada LED."""
        w = self.width
        if w <= 0:
            return
        led_w = w / self.num_leds
        now = Clock.get_time()
        
        for i in range(self.num_leds):
            led_center = i * led_w + led_w / 2
            brightness = 0.02  # Mínimo brillo (LED apagado)
            
            if self.state == SCAN_SPEAK:
                # Onda expansiva desde el centro (voz)
                center = w / 2
                dist = abs(led_center - center) * 0.04
                wave = math.sin(dist - self.wave_offset * 3)
                brightness = max(0.02, 0.2 + 0.8 * (wave * 0.5 + 0.5))
                # Atenuación hacia los bordes
                fade = 1.0 - (abs(led_center - center) / (w / 2)) * 0.3
                brightness *= fade
                
            elif self.state == SCAN_THINK:
                # Parpadeo aleatorio tipo "pensando"
                seed = hash((i, int(now * 4))) % 1000
                _random.seed(seed)
                brightness = 0.1 + 0.9 * _random.random()
                # Algunos LEDs se quedan más encendidos
                if i % 3 == 0:
                    brightness = max(brightness, 0.5)
                    
            elif self.state == SCAN_ALERT:
                # Flash rápido de alerta
                flash = 0.5 + 0.5 * math.sin(now * 12)
                brightness = 0.3 if flash > 0 else 0.02
                # Todos parpadean al mismo tiempo
                brightness = 0.8 if (int(now * 6) % 2 == 0) else 0.02
                
            else:
                # Scanner normal (idle/listen)
                scan_center = self.scan_pos * w
                dist = abs(led_center - scan_center)
                
                # Efecto de estela (más LEDs encendidos cerca del centro)
                trail_width = led_w * 5
                if dist < trail_width:
                    brightness = max(0.02, 1.0 - (dist / trail_width) ** 0.6)
                    # Efecto de respiración en listen
                    if self.state == SCAN_LISTEN:
                        brightness *= (0.6 + 0.4 * self.pulse)
                        brightness = max(brightness, 0.15)  # Brillo mínimo más alto
                else:
                    # LEDs vecinos con brillo muy tenue
                    tail = max(0, 1.0 - dist / (trail_width * 3))
                    brightness = max(0.02, tail * 0.08)
            
            self.led_brightness[i] = max(0.0, min(1.0, brightness))
    
    def draw(self, *args):
        """Renderiza el scanner KITT completo."""
        self.canvas.clear()
        w = self.width
        h = self.height
        x = self.x
        y = self.y
        
        if w <= 0 or h <= 0:
            return
        
        with self.canvas:
            # === Fondo oscuro del dashboard ===
            Color(*c('bg_dash'))
            Rectangle(pos=self.pos, size=self.size)
            
            # === Línea de borde superior (fina) ===
            Color(*c('kitt_dim'), 0.8)
            Rectangle(pos=(x, y + h - 1), size=(w, 1))
            
            # === Línea de borde inferior ===
            Color(*c('kitt_dim'), 0.4)
            Rectangle(pos=(x, y), size=(w, 1))
            
            # === Paneles laterales decorativos ===
            # Panel izquierdo (cuadrícula)
            Color(0.02, 0.02, 0.04, 1)
            Rectangle(pos=(x + 3, y + 5), size=(18, h - 30))
            # Indicador rojo pequeño
            Color(*c('kitt_dim'))
            Rectangle(pos=(x + 5, y + h - 20), size=(4, 4))
            Color(*c('kitt_red'), 0.3)
            Rectangle(pos=(x + 5, y + h - 20), size=(4, 4))
            # Segundo indicador
            Color(*c('amber_dim'))
            Rectangle(pos=(x + 13, y + h - 20), size=(4, 4))
            Color(*c('amber'), 0.2)
            Rectangle(pos=(x + 13, y + h - 20), size=(4, 4))
            
            # Panel derecho (simétrico)
            Color(0.02, 0.02, 0.04, 1)
            Rectangle(pos=(x + w - 21, y + 5), size=(18, h - 30))
            Color(*c('blue_dim'))
            Rectangle(pos=(x + w - 16, y + h - 20), size=(4, 4))
            Color(*c('blue'), 0.2)
            Rectangle(pos=(x + w - 16, y + h - 20), size=(4, 4))
            Color(*c('green_dim'))
            Rectangle(pos=(x + w - 8, y + h - 20), size=(4, 4))
            Color(*c('green'), 0.2)
            Rectangle(pos=(x + w - 8, y + h - 20), size=(4, 4))
            
            # === Scanner Bar (24 LEDs) ===
            led_margin = dp(22)
            led_area_w = w - led_margin * 2
            if led_area_w <= 0:
                return
            led_w = led_area_w / self.num_leds
            bar_y = y + h * 0.28
            bar_h = h * 0.40
            
            # Fondo de la barra de LEDs (receptor oscuro)
            Color(0.02, 0.0, 0.0, 1)
            Rectangle(pos=(x + led_margin - 2, bar_y - 3), size=(led_area_w + 4, bar_h + 6))
            Color(0.04, 0.0, 0.0, 0.5)
            Rectangle(pos=(x + led_margin - 1, bar_y - 2), size=(led_area_w + 2, bar_h + 4))
            
            # LEDs
            for i in range(self.num_leds):
                b = self.led_brightness[i]
                led_x = x + led_margin + i * led_w
                led_wi = max(1, led_w - 1.5)
                
                # Color KITT: rojo intenso con brillo variable
                r = min(1.0, b * 1.2)
                g = b * 0.03
                b_val = b * 0.03
                
                # LED principal
                Color(r, g, b_val, 0.95)
                Rectangle(pos=(led_x, bar_y), size=(led_wi, bar_h))
                
                # Resplandor exterior (si el LED está activo)
                if b > 0.3:
                    glow_size = 4 * b
                    Color(r * 0.3, g * 0.3, b_val * 0.3, b * 0.12)
                    Rectangle(pos=(led_x - glow_size, bar_y - glow_size), 
                              size=(led_wi + glow_size * 2, bar_h + glow_size * 2))
                
                # Centro brillante (punto caliente)
                if b > 0.6:
                    Color(min(1, r * 0.6), min(0.5, g), min(0.5, b_val), 0.4)
                    Rectangle(pos=(led_x + led_wi * 0.2, bar_y + bar_h * 0.2), 
                              size=(led_wi * 0.6, bar_h * 0.6))
            
            # === Reflector/cristal superior ===
            Color(1, 1, 1, 0.015)
            Rectangle(pos=(x + led_margin + 10, y + h - 15), size=(led_area_w - 20, 3))
            Color(1, 1, 1, 0.008)
            Rectangle(pos=(x + led_margin + 30, y + h - 10), size=(led_area_w - 60, 1))
            
            # === "NARIZ" de KITT (detalle central inferior) ===
            center_x = x + w / 2
            # Forma triangular estilizada
            Color(*c('kitt_dim'), 0.5)
            Rectangle(pos=(center_x - 12, y + 4), size=(24, 6))
            Color(*c('kitt_red'), 0.15)
            Rectangle(pos=(center_x - 6, y + 2), size=(12, 10))
            # Luz central roja (late con el scanner)
            pulse_intensity = 0.1 + 0.9 * (sum(self.led_brightness) / len(self.led_brightness))
            Color(*c('kitt_red'), 0.2 * pulse_intensity)
            Rectangle(pos=(center_x - 2, y + 4), size=(4, 4))
            
            # === Brillo ambiental general ===
            avg_bright = sum(self.led_brightness) / len(self.led_brightness)
            if avg_bright > 0.05:
                Color(1, 0.0, 0.0, avg_bright * 0.03)
                Rectangle(pos=(x, y), size=(w, h))
    
    def on_size(self, *args):
        """Redibujar cuando cambia el tamaño."""
        self.draw()
    
    def on_pos(self, *args):
        """Redibujar cuando cambia la posición."""
        self.draw()
