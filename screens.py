"""
Pantallas del Igor KITT App - Chat, Notas, Calendario, Casa, Config
"""
import json
import os
import threading
from datetime import datetime
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from kitt_theme import *
from kitt_face import KittFace

# Config
DEFAULT_SERVER = "http://localhost:5500"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "kitt_config.json")

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return {"server": DEFAULT_SERVER, "user": "vanadio"}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)


# ============================================================
#  WIDGETS COMPARTIDOS
# ============================================================

class KITTLabel(Label):
    """Label con estilo KITT - rojo, monospace."""
    def __init__(self, text="", kitt_color='kitt_red', font_size=sp(14), **kwargs):
        super().__init__(
            text=text,
            color=get_color_from_hex(COLORS.get(kitt_color, '#ff1a1a')),
            font_size=font_size,
            font_name='monospace',
            halign='center',
            valign='middle',
            **kwargs
        )

class KITTSeparator(Widget):
    """Línea separadora estilo KITT."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(*c('kitt_dim'), 0.6)
            Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*c('kitt_dim'), 0.6)
            Rectangle(pos=self.pos, size=self.size)

class KITTButton(Button):
    """Botón estilo KITT - fondo oscuro, texto rojo."""
    def __init__(self, text="", **kwargs):
        super().__init__(
            text=text,
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface2']),
            color=get_color_from_hex(COLORS['kitt_red']),
            font_name='monospace',
            font_size=sp(12),
            **kwargs
        )
        self.bind(state=self._on_state)
    
    def _on_state(self, instance, value):
        if value == 'down':
            self.background_color = get_color_from_hex(COLORS['kitt_dim'])
        else:
            self.background_color = get_color_from_hex(COLORS['surface2'])

class StatusBar(BoxLayout):
    """Barra de estado superior con info del sistema."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(STATUS_BAR_HEIGHT)
        self.padding = [dp(8), dp(2)]
        self.spacing = dp(4)
        
        with self.canvas.before:
            Color(*c('surface'))
            Rectangle(pos=self.pos, size=self.size)
            Color(*c('kitt_dim'), 0.3)
            Rectangle(pos=(self.x, self.y), size=(self.width, 1))
        
        self.config = load_config()
        
        # Usuario
        self.user_lbl = Label(
            text=f"OPERADOR: {self.config.get('user', '???').upper()}",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(9),
            font_name='monospace',
            size_hint_x=0.35,
            halign='left',
            valign='middle',
        )
        self.add_widget(self.user_lbl)
        
        # Conexión
        self.conn_lbl = Label(
            text="⚡ ONLINE",
            color=get_color_from_hex(COLORS['green']),
            font_size=sp(8),
            font_name='monospace',
            size_hint_x=0.3,
            halign='center',
            valign='middle',
        )
        self.add_widget(self.conn_lbl)
        
        # Reloj
        self.clock_lbl = Label(
            text="",
            color=get_color_from_hex(COLORS['text_dimmer']),
            font_size=sp(8),
            font_name='monospace',
            size_hint_x=0.35,
            halign='right',
            valign='middle',
        )
        self.add_widget(self.clock_lbl)
        
        Clock.schedule_interval(self._update_clock, 1)
    
    def _update_clock(self, dt):
        self.clock_lbl.text = datetime.now().strftime("%H:%M:%S")
    
    def update_user(self, user):
        self.user_lbl.text = f"OPERADOR: {user.upper()}"


# ============================================================
#  BURBUJA DE MENSAJE (CHAT)
# ============================================================
class MessageBubble(BoxLayout):
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(6), dp(3)]
        self.spacing = dp(6)
        
        msg_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, None),
            padding=[dp(10), dp(8)],
        )
        msg_box.bind(minimum_height=msg_box.setter('height'))
        
        # Borde del mensaje
        with msg_box.canvas.before:
            if is_user:
                Color(*c('user_msg_border'), 0.6)
            else:
                Color(*c('assistant_msg_border'), 0.6)
            RoundedRectangle(pos=msg_box.pos, size=msg_box.size, radius=[dp(6)])
            if is_user:
                Color(*c('user_msg'), 0.9)
            else:
                Color(*c('assistant_msg'), 0.9)
            RoundedRectangle(pos=(msg_box.x + 1, msg_box.y + 1), 
                           size=(msg_box.width - 2, msg_box.height - 2), 
                           radius=[dp(6)])
        
        # Etiqueta de rol
        role_lbl = Label(
            text="TÚ" if is_user else "IGOR",
            color=get_color_from_hex(COLORS['kitt_red'] if not is_user else COLORS['text_dimmer']),
            font_size=sp(8),
            font_name='monospace',
            size_hint_y=None,
            height=dp(14),
            halign='left',
            valign='middle',
            text_size=(msg_box.width - dp(10), None),
        )
        msg_box.add_widget(role_lbl)
        
        # Texto del mensaje
        text_lbl = Label(
            text=text,
            color=get_color_from_hex(COLORS['text']),
            font_size=sp(13),
            size_hint_y=None,
            text_size=(self.width * 0.65, None),
            halign='left',
            valign='top',
        )
        text_lbl.bind(texture_size=text_lbl.setter('size'))
        msg_box.add_widget(text_lbl)
        
        # Timestamp
        time_lbl = Label(
            text=datetime.now().strftime("%H:%M"),
            color=get_color_from_hex(COLORS['text_dimmer']),
            font_size=sp(7),
            font_name='monospace',
            size_hint_y=None,
            height=dp(12),
            halign='right',
            valign='middle',
        )
        msg_box.add_widget(time_lbl)
        
        # Layout
        if is_user:
            self.add_widget(Widget(size_hint_x=0.2))
            self.add_widget(msg_box)
        else:
            self.add_widget(msg_box)
            self.add_widget(Widget(size_hint_x=0.2))
        
        self.bind(size=self._update_text_width)
    
    def _update_text_width(self, *args):
        pass  # Placeholder


# ============================================================
#  PANTALLA 1: CHAT
# ============================================================
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Status Bar
        self.status_bar = StatusBar()
        layout.add_widget(self.status_bar)
        
        # KITT Face
        self.kitt_face = KittFace()
        layout.add_widget(self.kitt_face)
        
        # Header del chat
        header = BoxLayout(size_hint_y=None, height=dp(28), padding=[dp(10), 0])
        with header.canvas:
            Color(*c('surface'))
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(Label(
            text="> TERMINAL DE COMUNICACIONES",
            color=get_color_from_hex(COLORS['text_red']),
            font_size=sp(10), font_name='monospace',
            halign='left', valign='middle',
        ))
        layout.add_widget(header)
        
        # Chat Area (scroll)
        self.chat_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
            bar_color=get_color_from_hex(COLORS['kitt_dim']),
        )
        self.chat_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(4), dp(4)],
            spacing=dp(2),
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))
        self.chat_scroll.add_widget(self.chat_container)
        layout.add_widget(self.chat_scroll)
        
        # Mensajes de bienvenida KITT
        self._add_msg("IGOR KITT v1.0 — SISTEMA OPERATIVO", False)
        self._add_msg("Todos los sistemas funcionales. Escáner activo.", False)
        self._add_msg(f"Bienvenido, {self.config.get('user', 'Vanadio')}. ¿En qué puedo ayudarte?", False)
        
        # Input Area
        input_box = BoxLayout(
            size_hint_y=None, height=dp(INPUT_HEIGHT),
            padding=[dp(4), dp(3)],
            spacing=dp(4),
        )
        with input_box.canvas.before:
            Color(*c('surface'))
            Rectangle(pos=input_box.pos, size=input_box.size)
            Color(*c('kitt_dim'), 0.4)
            Rectangle(pos=(input_box.x, input_box.y + input_box.height - 1), 
                     size=(input_box.width, 1))
        
        self.text_input = TextInput(
            size_hint=(0.78, 1),
            hint_text="> COMANDO...",
            hint_text_color=get_color_from_hex(COLORS['text_dimmer']),
            foreground_color=get_color_from_hex(COLORS['text']),
            background_color=get_color_from_hex(COLORS['surface2']),
            cursor_color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(13),
            font_name='monospace',
            padding=[dp(10), dp(12)],
            multiline=False,
        )
        self.text_input.bind(on_text_validate=self._send_msg)
        
        send_btn = Button(
            text="▶ EJECUTAR",
            size_hint=(0.22, 1),
            background_color=get_color_from_hex(COLORS['kitt_red']),
            background_normal='',
            color=get_color_from_hex('#ffffff'),
            font_size=sp(9),
            font_name='monospace',
        )
        send_btn.bind(on_press=self._send_msg)
        
        input_box.add_widget(self.text_input)
        input_box.add_widget(send_btn)
        layout.add_widget(input_box)
        
        self.add_widget(layout)
    
    def _add_msg(self, text, is_user):
        bubble = MessageBubble(text, is_user)
        self.chat_container.add_widget(bubble)
        Clock.schedule_once(lambda dt: self._scroll_end(), 0.05)
    
    def _scroll_end(self):
        self.chat_scroll.scroll_y = 0
    
    def _send_msg(self, instance):
        text = self.text_input.text.strip()
        if not text:
            return
        
        self._add_msg(text, True)
        self.text_input.text = ''
        
        # KITT escucha -> piensa
        self.kitt_face.set_state(SCAN_LISTEN)
        Clock.schedule_once(lambda dt: self.kitt_face.set_state(SCAN_THINK), 0.3)
        
        threading.Thread(target=self._query_igor, args=(text,), daemon=True).start()
    
    def _response_done(self, reply):
        self._add_msg(reply, False)
        self.kitt_face.set_state(SCAN_SPEAK)
        duration = max(1.5, min(5.0, len(reply) * 0.04))
        Clock.schedule_once(lambda dt: self.kitt_face.set_state(SCAN_IDLE), duration)
    
    def _query_igor(self, text):
        try:
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            user = self.config.get("user", "vanadio")
            
            # Detectar nota
            if any(text.lower().startswith(p) for p in ["apunta", "nota:", "idea:", "guarda esto"]):
                contenido = text.split(" ", 1)[1] if " " in text else text
                try:
                    r = httpx.post(f"{server}/api/notas", json={
                        "user": user, "categoria": "General",
                        "titulo": contenido[:50], "contenido": contenido
                    }, timeout=5)
                    if r.json().get("ok"):
                        Clock.schedule_once(lambda dt: self._response_done("✅ Nota guardada."))
                        return
                except:
                    pass
                Clock.schedule_once(lambda dt: self._response_done("⚠️ Error al guardar nota."))
                return
            
            # Contexto de memoria
            ctx = ""
            try:
                r = httpx.get(f"{server}/api/memory/context?user={user}&limit=4", timeout=3)
                if r.status_code == 200 and r.json().get("context"):
                    ctx = "\n[CONTEXTO]\n" + r.json()["context"]
            except:
                pass
            
            prompt = "Eres KITT, el coche inteligente de Knight Rider. Hablas como KITT: calmado, seguro, con un toque de humor seco. Respuestas directas pero con estilo." + ctx
            
            # Proxy /api/chat
            r = httpx.post(f"{server}/api/chat", json={
                "model": "github-models/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                "max_tokens": 1024,
                "temperature": 0.7,
            }, timeout=60)
            
            if r.status_code == 200:
                data = r.json()
                if data.get("choices"):
                    reply = data["choices"][0]["message"]["content"]
                else:
                    reply = data.get("text", "⚠️ Sin respuesta")
                Clock.schedule_once(lambda dt: self._response_done(reply))
            else:
                Clock.schedule_once(lambda dt: self._response_done(f"⚠️ Error del sistema: {r.status_code}"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._response_done(f"⚠️ Fallo en comunicación: {str(e)}"))


# ============================================================
#  PANTALLA 2: NOTAS
# ============================================================
class NotasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Status bar
        StatusBar(size_hint_y=None, height=dp(STATUS_BAR_HEIGHT))
        layout.add_widget(StatusBar(size_hint_y=None, height=dp(STATUS_BAR_HEIGHT)))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(32), padding=[dp(10), 0])
        with header.canvas:
            Color(*c('surface'))
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(Label(
            text="> BLOG DE NOTAS // KITT DATABASE",
            color=get_color_from_hex(COLORS['text_red']),
            font_size=sp(10), font_name='monospace',
            halign='left', valign='middle',
        ))
        layout.add_widget(header)
        
        # Selector de categoría
        cat_row = BoxLayout(size_hint_y=None, height=dp(36), padding=[dp(6), dp(4)], spacing=dp(4))
        with cat_row.canvas:
            Color(*c('bg'))
            Rectangle(pos=cat_row.pos, size=cat_row.size)
        cat_row.add_widget(Label(
            text="CAT:",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(10), font_name='monospace',
            size_hint_x=0.15,
        ))
        self.cat_label = Label(
            text="Todas",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(11), font_name='monospace',
            size_hint_x=0.6, halign='left',
        )
        cat_row.add_widget(self.cat_label)
        self.cat_btn = Button(
            text="↻",
            size_hint_x=0.25,
            background_normal='',
            background_color=get_color_from_hex(COLORS['kitt_dim']),
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(16),
        )
        self.cat_btn.bind(on_press=self._cycle_category)
        cat_row.add_widget(self.cat_btn)
        layout.add_widget(cat_row)
        
        # Lista de notas
        self.notas_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
        )
        self.notas_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(6), dp(4)],
            spacing=dp(4),
        )
        self.notas_container.bind(minimum_height=self.notas_container.setter('height'))
        self.notas_scroll.add_widget(self.notas_container)
        layout.add_widget(self.notas_scroll)
        
        # Input nueva nota + botón
        input_row = BoxLayout(size_hint_y=None, height=dp(44), padding=[dp(4), dp(3)], spacing=dp(4))
        with input_row.canvas.before:
            Color(*c('surface'))
            Rectangle(pos=input_row.pos, size=input_row.size)
        
        self.nota_input = TextInput(
            size_hint=(0.7, 1),
            hint_text="Nueva nota...",
            hint_text_color=get_color_from_hex(COLORS['text_dimmer']),
            foreground_color=get_color_from_hex(COLORS['text']),
            background_color=get_color_from_hex(COLORS['surface2']),
            cursor_color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(12), font_name='monospace',
            padding=[dp(8), dp(10)],
            multiline=False,
        )
        add_btn = Button(
            text="+ NOTA",
            size_hint=(0.3, 1),
            background_color=get_color_from_hex(COLORS['kitt_red']),
            background_normal='',
            color=get_color_from_hex('#ffffff'),
            font_size=sp(9), font_name='monospace',
        )
        add_btn.bind(on_press=self._add_nota)
        
        input_row.add_widget(self.nota_input)
        input_row.add_widget(add_btn)
        layout.add_widget(input_row)
        
        self.add_widget(layout)
        
        # Cargar notas al iniciar
        self.categorias = []
        self.cat_index = 0
        Clock.schedule_once(lambda dt: self._load_notas(), 0.5)
    
    def _cycle_category(self, instance):
        if not self.categorias:
            return
        self.cat_index = (self.cat_index + 1) % (len(self.categorias) + 1)
        if self.cat_index == 0:
            self.cat_label.text = "Todas"
        else:
            self.cat_label.text = self.categorias[self.cat_index - 1]
        self._load_notas()
    
    def _load_notas(self):
        def load():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            user = self.config.get("user", "vanadio")
            
            try:
                # Cargar categorías
                r = httpx.get(f"{server}/api/notas/categorias?user={user}", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict) and data.get("categorias"):
                        self.categorias = data["categorias"]
                
                # Cargar notas
                url = f"{server}/api/notas?user={user}"
                if self.cat_label.text != "Todas":
                    url += f"&categoria={self.cat_label.text}"
                r = httpx.get(url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    notas = data.get("notas", []) if isinstance(data, dict) else data
                    Clock.schedule_once(lambda dt: self._render_notas(notas))
                else:
                    Clock.schedule_once(lambda dt: self._show_error("Error al cargar notas"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _render_notas(self, notas):
        self.notas_container.clear_widgets()
        
        if not notas:
            lbl = Label(
                text="[ NO HAY NOTAS ]",
                color=get_color_from_hex(COLORS['text_dimmer']),
                font_size=sp(14), font_name='monospace',
                size_hint_y=None, height=dp(60),
            )
            self.notas_container.add_widget(lbl)
            return
        
        for nota in notas:
            self._add_nota_card(nota)
    
    def _add_nota_card(self, nota):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(6)],
            spacing=dp(2),
        )
        card.bind(minimum_height=card.setter('height'))
        
        with card.canvas.before:
            Color(*c('surface'))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
            Color(*c('kitt_dim'), 0.3)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(6)), width=1)
        
        # Categoría badge
        cat = nota.get('categoria', 'General')
        cat_lbl = Label(
            text=f"[ {cat.upper()} ]",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(8), font_name='monospace',
            size_hint_y=None, height=dp(16),
            halign='left', valign='middle',
        )
        card.add_widget(cat_lbl)
        
        # Contenido
        contenido = nota.get('contenido', nota.get('titulo', ''))
        text_lbl = Label(
            text=contenido,
            color=get_color_from_hex(COLORS['text']),
            font_size=sp(12), font_name='monospace',
            size_hint_y=None,
            text_size=(self.width * 0.85, None),
            halign='left', valign='top',
        )
        text_lbl.bind(texture_size=text_lbl.setter('size'))
        card.add_widget(text_lbl)
        
        # Fecha
        fecha = nota.get('created_at', '')[:10]
        if fecha:
            fecha_lbl = Label(
                text=fecha,
                color=get_color_from_hex(COLORS['text_dimmer']),
                font_size=sp(7), font_name='monospace',
                size_hint_y=None, height=dp(14),
                halign='right', valign='middle',
            )
            card.add_widget(fecha_lbl)
        
        self.notas_container.add_widget(card)
    
    def _add_nota(self, instance):
        text = self.nota_input.text.strip()
        if not text:
            return
        
        def add():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            user = self.config.get("user", "vanadio")
            categoria = self.cat_label.text if self.cat_label.text != "Todas" else "General"
            try:
                r = httpx.post(f"{server}/api/notas", json={
                    "user": user, "categoria": categoria,
                    "titulo": text[:50], "contenido": text
                }, timeout=5)
                if r.json().get("ok"):
                    Clock.schedule_once(lambda dt: self._nota_added())
                else:
                    Clock.schedule_once(lambda dt: self._show_error("Error al guardar"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))
        
        self.nota_input.text = ''
        threading.Thread(target=add, daemon=True).start()
    
    def _nota_added(self):
        self._load_notas()
    
    def _show_error(self, msg):
        lbl = Label(
            text=f"⚠️ {msg}",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(12), font_name='monospace',
            size_hint_y=None, height=dp(30),
        )
        self.notas_container.add_widget(lbl)
        Clock.schedule_once(lambda dt: self._load_notas(), 3)


# ============================================================
#  PANTALLA 3: CALENDARIO
# ============================================================
class CalendarioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Status bar
        layout.add_widget(StatusBar(size_hint_y=None, height=dp(STATUS_BAR_HEIGHT)))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(32), padding=[dp(10), 0])
        with header.canvas:
            Color(*c('surface'))
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(Label(
            text="> CALENDARIO // PLAN DE MISIÓN",
            color=get_color_from_hex(COLORS['text_red']),
            font_size=sp(10), font_name='monospace',
            halign='left', valign='middle',
        ))
        layout.add_widget(header)
        
        # Lista de eventos
        self.event_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
        )
        self.event_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(6), dp(4)],
            spacing=dp(4),
        )
        self.event_container.bind(minimum_height=self.event_container.setter('height'))
        self.event_scroll.add_widget(self.event_container)
        layout.add_widget(self.event_scroll)
        
        # Input nuevo evento
        input_row = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(4), dp(3)],
            spacing=dp(3),
        )
        with input_row.canvas.before:
            Color(*c('surface'))
            Rectangle(pos=input_row.pos, size=input_row.size)
            Color(*c('kitt_dim'), 0.4)
            Rectangle(pos=(input_row.x, input_row.y + input_row.height - 1), 
                     size=(input_row.width, 1))
        
        self.event_input = TextInput(
            size_hint_y=None, height=dp(36),
            hint_text='Nuevo evento: "evento" o "el viernes a las 10: evento"',
            hint_text_color=get_color_from_hex(COLORS['text_dimmer']),
            foreground_color=get_color_from_hex(COLORS['text']),
            background_color=get_color_from_hex(COLORS['surface2']),
            cursor_color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(11), font_name='monospace',
            padding=[dp(8), dp(8)],
            multiline=False,
        )
        input_row.add_widget(self.event_input)
        
        btn_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        add_btn = Button(
            text="+ EVENTO",
            size_hint_x=0.5,
            background_color=get_color_from_hex(COLORS['kitt_red']),
            background_normal='',
            color=get_color_from_hex('#ffffff'),
            font_size=sp(9), font_name='monospace',
        )
        add_btn.bind(on_press=self._add_evento)
        refresh_btn = Button(
            text="↻",
            size_hint_x=0.5,
            background_color=get_color_from_hex(COLORS['surface2']),
            background_normal='',
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(14),
        )
        refresh_btn.bind(on_press=lambda x: self._load_eventos())
        btn_row.add_widget(add_btn)
        btn_row.add_widget(refresh_btn)
        input_row.add_widget(btn_row)
        layout.add_widget(input_row)
        
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self._load_eventos(), 0.5)
    
    def _load_eventos(self):
        def load():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            user = self.config.get("user", "vanadio")
            try:
                r = httpx.get(f"{server}/api/calendario/proximos?user={user}&limite=20", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    eventos = data.get("eventos", []) if isinstance(data, dict) else []
                    Clock.schedule_once(lambda dt: self._render_eventos(eventos))
                else:
                    Clock.schedule_once(lambda dt: self._show_cal_error("Error al cargar eventos"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_cal_error(str(e)))
        threading.Thread(target=load, daemon=True).start()
    
    def _render_eventos(self, eventos):
        self.event_container.clear_widgets()
        
        if not eventos:
            lbl = Label(
                text="[ NO HAY EVENTOS PROGRAMADOS ]",
                color=get_color_from_hex(COLORS['text_dimmer']),
                font_size=sp(12), font_name='monospace',
                size_hint_y=None, height=dp(60),
            )
            self.event_container.add_widget(lbl)
            return
        
        for ev in eventos:
            self._add_event_card(ev)
    
    def _add_event_card(self, ev):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(6)],
            spacing=dp(2),
        )
        card.bind(minimum_height=card.setter('height'))
        
        with card.canvas.before:
            Color(*c('surface'))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
            Color(*c('kitt_dim'), 0.3)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(6)), width=1)
        
        # Fecha
        fecha = ev.get('fecha', '???')
        hora = ev.get('hora_inicio', '')
        date_lbl = Label(
            text=f"> {fecha}  {hora}",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(10), font_name='monospace',
            size_hint_y=None, height=dp(18),
            halign='left', valign='middle',
        )
        card.add_widget(date_lbl)
        
        # Título
        titulo = ev.get('titulo', ev.get('descripcion', ''))
        text_lbl = Label(
            text=titulo,
            color=get_color_from_hex(COLORS['text']),
            font_size=sp(12), font_name='monospace',
            size_hint_y=None,
            text_size=(self.width * 0.85, None),
            halign='left', valign='top',
        )
        text_lbl.bind(texture_size=text_lbl.setter('size'))
        card.add_widget(text_lbl)
        
        # Tipo + recurrencia
        tipo = ev.get('tipo', 'personal')
        recurrencia = ev.get('recurrencia', '')
        meta_lbl = Label(
            text=f"[ {tipo.upper()} ] {recurrencia}",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(8), font_name='monospace',
            size_hint_y=None, height=dp(14),
            halign='left', valign='middle',
        )
        card.add_widget(meta_lbl)
        
        self.event_container.add_widget(card)
    
    def _add_evento(self, instance):
        text = self.event_input.text.strip()
        if not text:
            return
        
        def add():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            user = self.config.get("user", "vanadio")
            try:
                r = httpx.post(f"{server}/api/calendario", json={
                    "user": user,
                    "titulo": text,
                    "tipo": "personal",
                }, timeout=5)
                if r.json().get("ok"):
                    Clock.schedule_once(lambda dt: self._evento_added())
                else:
                    Clock.schedule_once(lambda dt: self._show_cal_error("Error al crear evento"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_cal_error(str(e)))
        
        self.event_input.text = ''
        threading.Thread(target=add, daemon=True).start()
    
    def _evento_added(self):
        self._load_eventos()
    
    def _show_cal_error(self, msg):
        lbl = Label(
            text=f"⚠️ {msg}",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(12), font_name='monospace',
            size_hint_y=None, height=dp(30),
        )
        self.event_container.add_widget(lbl)


# ============================================================
#  PANTALLA 4: CASA (SMART HOME)
# ============================================================
class CasaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Status bar
        layout.add_widget(StatusBar(size_hint_y=None, height=dp(STATUS_BAR_HEIGHT)))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(32), padding=[dp(10), 0])
        with header.canvas:
            Color(*c('surface'))
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(Label(
            text="> SMART HOME // CONTROL DEL HOGAR",
            color=get_color_from_hex(COLORS['text_red']),
            font_size=sp(10), font_name='monospace',
            halign='left', valign='middle',
        ))
        layout.add_widget(header)
        
        # Panel de dispositivos
        self.dev_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
        )
        self.dev_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(6)],
            spacing=dp(6),
        )
        self.dev_container.bind(minimum_height=self.dev_container.setter('height'))
        self.dev_scroll.add_widget(self.dev_container)
        layout.add_widget(self.dev_scroll)
        
        # Botón refresh
        btn_row = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(8), dp(4)])
        with btn_row.canvas.before:
            Color(*c('surface'))
            Rectangle(pos=btn_row.pos, size=btn_row.size)
        
        refresh_btn = Button(
            text="↻ ESCANEAR DISPOSITIVOS",
            size_hint_x=1,
            background_color=get_color_from_hex(COLORS['kitt_dim']),
            background_normal='',
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(10), font_name='monospace',
        )
        refresh_btn.bind(on_press=lambda x: self._load_devices())
        btn_row.add_widget(refresh_btn)
        layout.add_widget(btn_row)
        
        self.add_widget(layout)
        
        Clock.schedule_once(lambda dt: self._load_devices(), 0.5)
    
    def _load_devices(self):
        self.dev_container.clear_widgets()
        loading = Label(
            text="> ESCANEANDO...",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(14), font_name='monospace',
            size_hint_y=None, height=dp(60),
        )
        self.dev_container.add_widget(loading)
        
        def load():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            try:
                # Obtener estado de todos los dispositivos
                r = httpx.get(f"{server}/api/smarthome", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    Clock.schedule_once(lambda dt: self._render_devices(data))
                else:
                    # Intentar con devices.json
                    try:
                        r2 = httpx.get(f"{server}/api/smarthome/status", timeout=5)
                        if r2.status_code == 200:
                            Clock.schedule_once(lambda dt: self._render_devices(r2.json()))
                            return
                    except:
                        pass
                    Clock.schedule_once(lambda dt: self._show_dev_error("No hay dispositivos o servidor sin respuesta"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_dev_error(f"Error: {str(e)[:50]}"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _render_devices(self, data):
        self.dev_container.clear_widgets()
        
        if isinstance(data, dict) and data.get("dispositivos"):
            dispositivos = data["dispositivos"]
        elif isinstance(data, list):
            dispositivos = data
        elif isinstance(data, dict):
            # Mostrar claves como dispositivos
            dispositivos = [{"nombre": k, "estado": v} for k, v in data.items() if k != "ok"]
        else:
            dispositivos = []
        
        if not dispositivos:
            lbl = Label(
                text="[ NO SE ENCONTRARON DISPOSITIVOS ]",
                color=get_color_from_hex(COLORS['text_dimmer']),
                font_size=sp(11), font_name='monospace',
                size_hint_y=None, height=dp(60),
            )
            self.dev_container.add_widget(lbl)
            return
        
        for dev in dispositivos:
            self._add_device_card(dev)
    
    def _add_device_card(self, dev):
        nombre = dev.get('nombre', dev.get('name', '?'))
        estado = dev.get('estado', dev.get('state', 'off'))
        is_on = estado in ('on', True, 'true', '1', 1)
        
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(56),
            padding=[dp(10), dp(6)],
            spacing=dp(8),
        )
        
        with card.canvas.before:
            Color(*c('surface'))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
            border_color = COLORS['green'] if is_on else COLORS['kitt_dim']
            Color(*get_color_from_hex(border_color), 0.3)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(8)), width=1)
        
        # Indicador LED
        led = Widget(size_hint=(0.1, 1))
        with led.canvas:
            Color(*c('green' if is_on else 'kitt_dim'), 0.8 if is_on else 0.3)
            RoundedRectangle(pos=(led.x + dp(6), led.y + dp(18)), 
                           size=(dp(12), dp(12)), radius=[dp(6)])
        card.add_widget(led)
        
        # Nombre
        name_lbl = Label(
            text=nombre.upper(),
            color=get_color_from_hex(COLORS['text']),
            font_size=sp(12), font_name='monospace',
            size_hint_x=0.6, halign='left', valign='middle',
        )
        card.add_widget(name_lbl)
        
        # Toggle button
        toggle_btn = Button(
            text="ENCENDER" if not is_on else "APAGAR",
            size_hint=(0.3, 0.8),
            background_color=get_color_from_hex(COLORS['green_dim'] if not is_on else COLORS['kitt_dim']),
            background_normal='',
            color=get_color_from_hex(COLORS['green'] if not is_on else COLORS['text']),
            font_size=sp(8), font_name='monospace',
            pos_hint={'center_y': 0.5},
        )
        toggle_btn.dev_nombre = nombre
        toggle_btn.bind(on_press=self._toggle_device)
        card.add_widget(toggle_btn)
        
        self.dev_container.add_widget(card)
    
    def _toggle_device(self, instance):
        nombre = instance.dev_nombre
        instance.text = "⏳"
        
        def toggle():
            import httpx
            server = self.config.get("server", DEFAULT_SERVER)
            try:
                r = httpx.post(f"{server}/api/smarthome/{nombre}", json={"action": "toggle"}, timeout=8)
                data = r.json()
                Clock.schedule_once(lambda dt: self._load_devices())
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_dev_error(f"Error: {str(e)[:40]}"))
        
        threading.Thread(target=toggle, daemon=True).start()
    
    def _show_dev_error(self, msg):
        self.dev_container.clear_widgets()
        lbl = Label(
            text=f"⚠️ {msg}",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(11), font_name='monospace',
            size_hint_y=None, height=dp(60),
        )
        self.dev_container.add_widget(lbl)


# ============================================================
#  PANTALLA 5: CONFIGURACIÓN / AJUSTES
# ============================================================
class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Status bar
        layout.add_widget(StatusBar(size_hint_y=None, height=dp(STATUS_BAR_HEIGHT)))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(32), padding=[dp(10), 0])
        with header.canvas:
            Color(*c('surface'))
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(Label(
            text="> CONFIGURACIÓN DEL SISTEMA",
            color=get_color_from_hex(COLORS['text_red']),
            font_size=sp(10), font_name='monospace',
            halign='left', valign='middle',
        ))
        layout.add_widget(header)
        
        # Contenido
        content = BoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12),
        )
        
        # Título
        title_lbl = Label(
            text="KITT v1.0",
            color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(22), font_name='monospace',
            size_hint_y=None, height=dp(36),
        )
        content.add_widget(title_lbl)
        
        # Separador
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(*c('kitt_dim'), 0.5)
            Rectangle(pos=sep.pos, size=sep.size)
        content.add_widget(sep)
        
        # Servidor
        content.add_widget(Label(
            text="SERVIDOR IGOR:",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(9), font_name='monospace',
            size_hint_y=None, height=dp(16),
            halign='left',
        ))
        self.server_input = TextInput(
            text=self.config.get("server", DEFAULT_SERVER),
            size_hint_y=None, height=dp(38),
            background_color=get_color_from_hex(COLORS['surface2']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(11), font_name='monospace',
            padding=[dp(8), dp(8)],
        )
        content.add_widget(self.server_input)
        
        # Usuario
        content.add_widget(Label(
            text="OPERADOR:",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(9), font_name='monospace',
            size_hint_y=None, height=dp(16),
            halign='left',
        ))
        self.user_input = TextInput(
            text=self.config.get("user", "vanadio"),
            size_hint_y=None, height=dp(38),
            background_color=get_color_from_hex(COLORS['surface2']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['kitt_red']),
            font_size=sp(11), font_name='monospace',
            padding=[dp(8), dp(8)],
        )
        content.add_widget(self.user_input)
        
        # Separador
        sep2 = Widget(size_hint_y=None, height=dp(1))
        with sep2.canvas:
            Color(*c('kitt_dim'), 0.5)
            Rectangle(pos=sep2.pos, size=sep2.size)
        content.add_widget(sep2)
        
        # Botones
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        
        detect_btn = Button(
            text="🔍 DETECTAR",
            size_hint_x=0.4,
            background_color=get_color_from_hex(COLORS['surface2']),
            background_normal='',
            color=get_color_from_hex(COLORS['amber']),
            font_size=sp(9), font_name='monospace',
        )
        detect_btn.bind(on_press=self._detect_connection)
        btn_row.add_widget(detect_btn)
        
        save_btn = Button(
            text="▶ GUARDAR",
            size_hint_x=0.6,
            background_color=get_color_from_hex(COLORS['kitt_red']),
            background_normal='',
            color=get_color_from_hex('#ffffff'),
            font_size=sp(10), font_name='monospace',
        )
        save_btn.bind(on_press=self._save_config)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)
        
        # Estado
        self.status_label = Label(
            text="",
            color=get_color_from_hex(COLORS['text_dim']),
            font_size=sp(9), font_name='monospace',
            size_hint_y=None, height=dp(20),
        )
        content.add_widget(self.status_label)
        
        # URL actual
        self.url_label = Label(
            text="",
            color=get_color_from_hex(COLORS['text_dimmer']),
            font_size=sp(8), font_name='monospace',
            size_hint_y=None, height=dp(30),
        )
        content.add_widget(self.url_label)
        
        content.add_widget(Widget())  # Spacer
        
        layout.add_widget(content)
        self.add_widget(layout)
        
        # Mostrar URL actual
        self._show_current_url()
    
    def _show_current_url(self):
        cfg = load_config()
        srv = cfg.get("server", DEFAULT_SERVER)
        self.url_label.text = f"SERVIDOR: {srv}"
    
    def _detect_connection(self, instance):
        self.status_label.text = "DETECTANDO..."
        threading.Thread(target=self._do_detect, daemon=True).start()
    
    def _do_detect(self):
        import httpx
        urls_to_try = [
            ("http://localhost:5500", "localhost"),
            ("http://127.0.0.1:5500", "local IP"),
            ("http://192.168.31.240:5500", "LAN"),
            ("https://lopez-approx-particle-married.trycloudflare.com", "túnel"),
        ]
        
        for url, label in urls_to_try:
            try:
                r = httpx.get(f"{url}/api/notas/categorias?user=vanadio", timeout=3)
                if r.status_code == 200:
                    Clock.schedule_once(lambda dt, u=url, l=label: self._found_server(u, l))
                    return
            except:
                continue
        
        Clock.schedule_once(lambda dt: self._no_server())
    
    def _found_server(self, url, label):
        self.server_input.text = url
        self.status_label.text = f"✔ CONECTADO VÍA {label.upper()}"
        self.status_label.color = get_color_from_hex(COLORS['green'])
    
    def _no_server(self):
        self.status_label.text = "✖ NO SE ENCONTRÓ SERVIDOR IGOR"
        self.status_label.color = get_color_from_hex(COLORS['kitt_red'])
    
    def _save_config(self, instance):
        cfg = {"server": self.server_input.text.strip(), "user": self.user_input.text.strip()}
        save_config(cfg)
        instance.text = "✔ GUARDADO"
        self._show_current_url()
        Clock.schedule_once(lambda dt: setattr(instance, 'text', '▶ GUARDAR'), 2)
