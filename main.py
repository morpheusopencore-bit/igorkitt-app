"""
Igor KITT - Knight Rider App
Entry point: Inicializa y lanza la interfaz KITT
"""
import os
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

from kitt_theme import *
from screens import ChatScreen, NotasScreen, CalendarioScreen, CasaScreen, ConfigScreen


class IgorKITTApp(App):
    title = "Igor KITT"
    icon = 'icon.png'
    
    def build(self):
        # Config Kivy
        Config.set('kivy', 'keyboard_mode', 'system')
        Config.set('graphics', 'width', '400')
        Config.set('graphics', 'height', '700')
        
        Window.clearcolor = get_color_from_hex(COLORS['bg'])
        
        # Screen Manager
        sm = ScreenManager()
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(NotasScreen(name='notas'))
        sm.add_widget(CalendarioScreen(name='calendario'))
        sm.add_widget(CasaScreen(name='casa'))
        sm.add_widget(ConfigScreen(name='config'))
        
        # Layout principal
        main = BoxLayout(orientation='vertical', spacing=0)
        main.add_widget(sm)
        
        # === Barra de navegación inferior estilo KITT ===
        nav = BoxLayout(size_hint_y=None, height=dp(NAV_HEIGHT))
        
        with nav.canvas.before:
            Color(*c('nav_bg'))
            Rectangle(pos=nav.pos, size=nav.size)
            # Línea roja superior (como la tira de LED de KITT)
            Color(*c('kitt_red'), 0.8)
            Rectangle(pos=(nav.x, nav.y + nav.height - 2), size=(nav.width, 2))
            # Sutil brillo debajo de la línea roja
            Color(*c('kitt_red'), 0.08)
            Rectangle(pos=(nav.x, nav.y + nav.height - 12), size=(nav.width, 10))
        
        items = [
            ("⚡", "chat", "CHAT"),
            ("📓", "notas", "NOTAS"),
            ("📅", "calendario", "DÍAS"),
            ("🏠", "casa", "CASA"),
            ("⚙", "config", "KITT"),
        ]
        
        for icon, sname, label in items:
            btn = Button(
                text=f"{icon}\n{label}",
                font_size=sp(8),
                font_name='monospace',
                color=get_color_from_hex(COLORS['nav_inactive']),
                background_color=get_color_from_hex(COLORS['nav_bg']),
                background_normal='',
                size_hint_x=0.2,
                markup=True,
            )
            btn.sname = sname
            
            # Resaltar botón activo
            def make_callback(name):
                def callback(instance):
                    sm.current = name
                    # Actualizar colores de todos los botones
                    for child in nav.children:
                        if hasattr(child, 'sname'):
                            if child.sname == name:
                                child.color = get_color_from_hex(COLORS['kitt_red'])
                            else:
                                child.color = get_color_from_hex(COLORS['nav_inactive'])
                return callback
            
            btn.bind(on_press=make_callback(sname))
            
            # Si es el primer botón, resaltarlo
            if sname == 'chat':
                btn.color = get_color_from_hex(COLORS['kitt_red'])
            
            nav.add_widget(btn)
        
        main.add_widget(nav)
        
        return main


if __name__ == "__main__":
    IgorKITTApp().run()
