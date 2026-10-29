from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from io import BytesIO
import requests
from style import *

class CartScreen(Screen):
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

    def load_cart(self):
        self.layout.clear_widgets()
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        btn_back = Button(text="< Назад", size_hint_x=None, width=100, background_color=BG_COLOR, color=PRIMARY, bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header.add_widget(btn_back)
        self.layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        items_layout = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        total_sum = 0
        items = []
        try:
            import main
            res = requests.get(f"{main.API_URL}/api/cart", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            items = res.json() if res.status_code == 200 else []
            if not items:
                items_layout.add_widget(Label(text="Корзина пуста", color=TEXT_COLOR, size_hint_y=None, height=100))
            for i in items:
                card = BoxLayout(size_hint_y=None, height=80, padding=5, spacing=5)
                with card.canvas.before:
                    Color(0.95, 0.95, 0.95, 1)
                    card.rect = Rectangle(pos=card.pos, size=card.size)
                card.bind(pos=lambda inst, val: setattr(card.rect, 'pos', val), size=lambda inst, val: setattr(card.rect, 'size', val))
                
                img_url = i.get('image_url', '')
                texture = self._get_texture(img_url)
                if texture:
                    img_widget = Image(texture=texture, size_hint=(None, 1), width=60, allow_stretch=True, keep_ratio=True)
                else:
                    img_widget = Label(text="Фото", size_hint=(None, 1), width=60, color=get_color_from_hex('#757575'))
                
                info = BoxLayout(orientation='vertical', size_hint_x=1)
                info.add_widget(Label(text=i['product_name'], color=TEXT_COLOR, bold=True, halign="left"))
                info.add_widget(Label(text=f"Размер: {i['size']} x {i['quantity']}", color=get_color_from_hex('#757575'), size_hint_y=None, height=20))
                
                price = i['price'] * i['quantity']
                total_sum += price
                right_side = BoxLayout(orientation='vertical', size_hint_x=None, width=100)
                right_side.add_widget(Label(text=f"{price:.0f} RUB", color=PRIMARY, bold=True))
                
                btn_remove = Button(text="Удалить", size_hint_y=None, height=30, background_color=get_color_from_hex('#EF5350'), color=(1,1,1,1), font_size=12)
                btn_remove.bind(on_press=lambda x, item_id=i['id']: self.remove_item(item_id))
                right_side.add_widget(btn_remove)
                
                card.add_widget(img_widget)
                card.add_widget(info)
                card.add_widget(right_side)
                items_layout.add_widget(card)
        except Exception as e:
            items_layout.add_widget(Label(text=f"Ошибка: {e}", color=TEXT_COLOR))
        
        scroll.add_widget(items_layout)
        self.layout.add_widget(scroll)
        
        if items:
            bottom_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=220, padding=10, spacing=5)
            bottom_panel.add_widget(Label(text=f"Итого: {total_sum:.0f} RUB", font_size=20, bold=True, color=TEXT_COLOR, size_hint_y=None, height=40))
            
            city_layout = BoxLayout(size_hint_y=None, height=45)
            city_layout.add_widget(Label(text="Город:", color=TEXT_COLOR, size_hint_x=0.3))
            self.city_spinner = Spinner(text='Москва', values=('Москва', 'СПб', 'Казань'), background_color=GRAY, color=TEXT_COLOR, size_hint_x=0.7)
            city_layout.add_widget(self.city_spinner)
            bottom_panel.add_widget(city_layout)
            
            pay_layout = BoxLayout(size_hint_y=None, height=45)
            pay_layout.add_widget(Label(text="Оплата:", color=TEXT_COLOR, size_hint_x=0.3))
            self.pay_spinner = Spinner(text='Наличные', values=('Наличные', 'Карта'), background_color=GRAY, color=TEXT_COLOR, size_hint_x=0.7)
            pay_layout.add_widget(self.pay_spinner)
            bottom_panel.add_widget(pay_layout)

            btn_checkout = Button(text="Оформить заказ", size_hint_y=None, height=50, background_color=PRIMARY, color=(1,1,1,1), font_size=18, bold=True)
            btn_checkout.bind(on_press=self.checkout)
            bottom_panel.add_widget(btn_checkout)
            
            self.layout.add_widget(bottom_panel)

    def remove_item(self, item_id):
        import main
        try:
            requests.delete(f"{main.API_URL}/api/cart/{item_id}", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            self.load_cart()
            self.manager.get_screen('main').update_cart_count()
        except: pass

    def checkout(self, instance):
        import main
        try:
            res = requests.post(f"{main.API_URL}/api/cart/checkout", json={"payment_method": self.pay_spinner.text, "city": self.city_spinner.text}, headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            if res.status_code == 200:
                Popup(title="Успех", content=Label(text="Заказ оформлен!"), size_hint=(0.7, 0.3), background_color=(1,1,1,1)).open()
                self.manager.get_screen('main').update_cart_count()
                self.manager.current = 'main'
            else:
                Popup(title="Ошибка", content=Label(text=f"Код: {res.status_code}"), size_hint=(0.7, 0.3), background_color=(1,1,1,1)).open()
        except Exception as e:
            Popup(title="Ошибка", content=Label(text=str(e)), size_hint=(0.7, 0.3), background_color=(1,1,1,1)).open()