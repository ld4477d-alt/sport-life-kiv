from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from io import BytesIO
import requests
from style import *


class OrdersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self._image_cache = {}

    def _get_texture(self, url):
        if not url or not str(url).strip():
            return None
        if url in self._image_cache:
            return self._image_cache[url].texture
        try:
            response = requests.get(url, timeout=3)
            if response.status_code != 200:
                return None
            core_img = CoreImage(BytesIO(response.content), ext="jpg")
            self._image_cache[url] = core_img
            return core_img.texture
        except:
            return None

    def on_enter(self):
        self.load_orders()

    def load_orders(self):
        import main
        self.layout.clear_widgets()

        # --- Шапка ---
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        btn_back = Button(text="< Назад", size_hint_x=None, width=100,
                          background_color=BG_COLOR, color=PRIMARY, bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'profile'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="МОИ ЗАКАЗЫ", font_size=20, bold=True, color=TEXT_COLOR))
        self.layout.add_widget(header)

        # --- Контейнер для заказов (БЕЗ ScrollView, чтобы не было багов с пустотой) ---
        # Используем GridLayout, который будет растягиваться по высоте
        content = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        try:
            res = requests.get(f"{main.API_URL}/api/orders",
                               headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            orders = res.json() if res.status_code == 200 else []

            if not orders:
                content.add_widget(Label(text="Нет заказов", color=TEXT_COLOR,
                                         size_hint_y=None, height=100))
            else:
                # Ограничиваем вывод 3 последними заказами, чтобы не улетели за экран
                for o in orders[:5]:
                    items = o.get('items', [])
                    # Высота: 50 (заголовок + статус) + 55 на товар + 20 отступы
                    card_height = 55 + (len(items) * 55) + 20

                    order_card = BoxLayout(orientation='vertical', spacing=5,
                                           size_hint_y=None, height=card_height, padding=10)

                    with order_card.canvas.before:
                        Color(0.95, 0.95, 0.95, 1)
                        order_card.rect = Rectangle(pos=order_card.pos, size=order_card.size)
                    order_card.bind(pos=lambda inst, val: setattr(order_card.rect, 'pos', val),
                                    size=lambda inst, val: setattr(order_card.rect, 'size', val))

                    order_card.add_widget(Label(text=f"Заказ #{o['id']} | {o.get('created_at', '')[:10]}",
                                                bold=True, color=TEXT_COLOR, size_hint_y=None, height=25))
                    order_card.add_widget(Label(text=f"Статус: {o.get('status', 'Pending')} | Сумма: {o.get('total_price', 0):.0f} ₽",
                                                color=PRIMARY, size_hint_y=None, height=25))

                    for item in items:
                        item_layout = BoxLayout(size_hint_y=None, height=55, spacing=10)

                        texture = self._get_texture(item.get('image_url'))
                        if texture:
                            img = Image(texture=texture, size_hint=(None, 1), width=50,
                                        allow_stretch=True, keep_ratio=True)
                        else:
                            img = Label(text="Фото", size_hint=(None, 1), width=50,
                                        color=get_color_from_hex('#757575'))
                        item_layout.add_widget(img)

                        item_info = BoxLayout(orientation='vertical')
                        item_info.add_widget(Label(text=item.get('product_name', ''),
                                                   color=TEXT_COLOR, bold=True))
                        item_info.add_widget(Label(text=f"{item.get('quantity')} шт. x {item.get('price'):.0f} ₽",
                                                   color=get_color_from_hex('#757575'),
                                                   size_hint_y=None, height=20))
                        item_layout.add_widget(item_info)

                        order_card.add_widget(item_layout)

                    content.add_widget(order_card)
        except Exception as e:
            content.add_widget(Label(text=f"Ошибка: {e}", color=ERROR,
                                     size_hint_y=None, height=100))

        # Оборачиваем в ScrollView, чтобы можно было прокрутить, если заказов много
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(content)
        self.layout.add_widget(scroll)