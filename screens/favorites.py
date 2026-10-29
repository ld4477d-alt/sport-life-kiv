from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from io import BytesIO
import requests
from style import *

class FavoritesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self._image_cache = {}

    def _get_texture(self, url):
        if not url or not str(url).strip(): return None
        if url in self._image_cache: return self._image_cache[url].texture
        try:
            response = requests.get(url, timeout=3)
            if response.status_code != 200: return None
            core_img = CoreImage(BytesIO(response.content), ext="jpg")
            self._image_cache[url] = core_img
            return core_img.texture
        except: return None

    def on_enter(self):
        self.load_favorites()

    def load_favorites(self):
        import main
        self.layout.clear_widgets()
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        btn_back = Button(text="< Назад", size_hint_x=None, width=100, background_color=BG_COLOR, color=PRIMARY, bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="ИЗБРАННОЕ", font_size=20, bold=True, color=TEXT_COLOR))
        self.layout.add_widget(header)
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=10, padding=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        if not main.CURRENT_TOKEN:
            content.add_widget(Label(text="Войдите в аккаунт", color=TEXT_COLOR, size_hint_y=None, height=100))
        else:
            try:
                res = requests.get(f"{main.API_URL}/api/favorites", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
                favs = res.json() if res.status_code == 200 else []
                if not favs:
                    content.add_widget(Label(text="Список пуст", color=TEXT_COLOR, size_hint_y=None, height=100))
                else:
                    for f in favs:
                        card = BoxLayout(size_hint_y=None, height=80, padding=10, spacing=10)
                        with card.canvas.before:
                            Color(0.95, 0.95, 0.95, 1)
                            card.rect = Rectangle(pos=card.pos, size=card.size)
                        card.bind(pos=lambda inst, val: setattr(card.rect, 'pos', val), size=lambda inst, val: setattr(card.rect, 'size', val))
                        
                        texture = self._get_texture(f.get('image_url'))
                        if texture:
                            img = Image(texture=texture, size_hint=(None, 1), width=60, allow_stretch=True, keep_ratio=True)
                        else:
                            img = Label(text="Фото", size_hint=(None, 1), width=60, color=get_color_from_hex('#757575'))
                        card.add_widget(img)
                        
                        info = BoxLayout(orientation='vertical')
                        info.add_widget(Label(text=f.get('product_name', ''), bold=True, color=TEXT_COLOR))
                        info.add_widget(Label(text=f"{f.get('price', 0):.0f} ₽", color=PRIMARY))
                        card.add_widget(info)
                        
                        btn_remove = Button(text="Удалить", size_hint_x=None, width=100, background_color=DANGER, color=(1,1,1,1))
                        btn_remove.bind(on_press=lambda x, pid=f['product_id']: self.remove(pid))
                        card.add_widget(btn_remove)
                        content.add_widget(card)
            except Exception as e:
                content.add_widget(Label(text=f"Ошибка: {e}", color=ERROR))
        
        scroll.add_widget(content)
        self.layout.add_widget(scroll)

    def remove(self, product_id):
        import main
        try:
            requests.delete(f"{main.API_URL}/api/favorites/{product_id}", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            self.load_favorites()
        except: pass