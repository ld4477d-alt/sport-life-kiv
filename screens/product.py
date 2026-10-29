from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from io import BytesIO
import requests
from style import *

class ProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_data = None
        self._image_cache = {}
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

    def _detect_ext(self, url, content_type):
        url_l = (url or "").lower()
        ct = (content_type or "").lower()
        if url_l.endswith((".jpg", ".jpeg")) or "jpeg" in ct or "jpg" in ct:
            return "jpg"
        if url_l.endswith(".png") or "png" in ct:
            return "png"
        return None

    def _get_texture(self, url):
        if not url or not str(url).strip():
            return None
        if url in self._image_cache:
            return self._image_cache[url].texture
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return None
            ext = self._detect_ext(url, response.headers.get("Content-Type", ""))
            core_img = CoreImage(BytesIO(response.content), ext=ext)
            self._image_cache[url] = core_img
            return core_img.texture
        except Exception as e:
            return None

    def set_product(self, product):
        self.product_data = product
        self.render_product()

    def render_product(self):
        import main
        self.layout.clear_widgets()
        if not self.product_data:
            return
        p = self.product_data

        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        btn_back = Button(text="< Назад", size_hint_x=None, width=100, background_color=BG_COLOR, color=PRIMARY, bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header.add_widget(btn_back)
        self.layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, padding=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        texture = self._get_texture(p.get('image_url'))
        if texture:
            img = Image(texture=texture, size_hint_y=None, height=300, allow_stretch=True, keep_ratio=True)
            content.add_widget(img)
        else:
            content.add_widget(Label(text="Нет фото", color=get_color_from_hex('#757575'), size_hint_y=None, height=300))

        content.add_widget(Label(text=p.get('brand', ''), font_size=14, color=get_color_from_hex('#757575'), size_hint_y=None, height=20))

        name_lbl = Label(text=p['name'], font_size=22, bold=True, color=TEXT_COLOR, size_hint_y=None, height=40, halign='left')
        name_lbl.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        content.add_widget(name_lbl)

        price_text = (f"{p['price']:.0f} RUB" if p.get('in_stock', True) else "Нет в наличии")
        content.add_widget(Label(text=price_text, font_size=28, bold=True, color=PRIMARY if p.get('in_stock', True) else get_color_from_hex('#E53935'), size_hint_y=None, height=50))

        if p.get('description'):
            desc_text = Label(text=p['description'], font_size=14, color=TEXT_COLOR, size_hint_y=None, height=100, halign='left')
            desc_text.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
            content.add_widget(desc_text)

        if main.CURRENT_ROLE == "CUSTOMER" and p.get('in_stock', True):
            size_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
            size_layout.add_widget(Label(text="Размер:", color=TEXT_COLOR, size_hint_x=0.3))
            raw_sizes = p.get('sizes') or ''
            sizes = [s.strip() for s in str(raw_sizes).split(',') if s.strip()]
            self.size_spinner = Spinner(text=sizes[0] if sizes else 'M', values=sizes if sizes else ('XS', 'S', 'M', 'L', 'XL'), background_color=GRAY, color=TEXT_COLOR, size_hint_x=0.7)
            size_layout.add_widget(self.size_spinner)
            content.add_widget(size_layout)

            qty_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
            qty_layout.add_widget(Label(text="Количество:", color=TEXT_COLOR, size_hint_x=0.3))
            qty_box = BoxLayout(size_hint_x=0.7, spacing=5)
            self.qty_label = Label(text="1", color=TEXT_COLOR, font_size=18)
            btn_minus = Button(text="-", size_hint_x=0.3, background_color=GRAY, color=TEXT_COLOR)
            btn_minus.bind(on_press=lambda x: setattr(self.qty_label, 'text', str(max(1, int(self.qty_label.text) - 1))))
            btn_plus = Button(text="+", size_hint_x=0.3, background_color=GRAY, color=TEXT_COLOR)
            btn_plus.bind(on_press=lambda x: setattr(self.qty_label, 'text', str(int(self.qty_label.text) + 1)))
            qty_box.add_widget(btn_minus)
            qty_box.add_widget(self.qty_label)
            qty_box.add_widget(btn_plus)
            qty_layout.add_widget(qty_box)
            content.add_widget(qty_layout)

        scroll.add_widget(content)
        self.layout.add_widget(scroll)

        if p.get('in_stock', True) and main.CURRENT_ROLE == "CUSTOMER":
            btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
            
            btn_fav = Button(text="В избранное", size_hint_x=0.4, background_color=GRAY, color=PRIMARY, bold=True, font_size=14)
            btn_fav.bind(on_press=self.add_to_favorites)
            
            btn_add = Button(text="В корзину", size_hint_x=0.6, background_color=PRIMARY, color=(1, 1, 1, 1), bold=True, font_size=14)
            btn_add.bind(on_press=self.add_to_cart)
            
            btn_layout.add_widget(btn_fav)
            btn_layout.add_widget(btn_add)
            self.layout.add_widget(btn_layout)

        if main.CURRENT_ROLE == "ADMIN":
            admin_layout = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=(10, 5))
            btn_edit = Button(text="Редактировать", background_color=get_color_from_hex('#FFA726'), color=(1, 1, 1, 1), bold=True)
            btn_edit.bind(on_press=self.edit_product)
            btn_delete = Button(text="Удалить", background_color=get_color_from_hex('#EF5350'), color=(1, 1, 1, 1), bold=True)
            btn_delete.bind(on_press=self.confirm_delete)
            admin_layout.add_widget(btn_edit)
            admin_layout.add_widget(btn_delete)
            self.layout.add_widget(admin_layout)

    def add_to_favorites(self, instance):
        import main
        if not main.CURRENT_TOKEN:
            Popup(title="Ошибка", content=Label(text="Вы не авторизованы"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            return
        try:
            res = requests.post(f"{main.API_URL}/api/favorites/add", json={"product_id": self.product_data['id']}, headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            if res.status_code == 200:
                Popup(title="Успех", content=Label(text="Добавлено в избранное!"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            elif res.status_code == 400:
                Popup(title="Внимание", content=Label(text="Уже в избранном"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            else:
                Popup(title="Ошибка", content=Label(text=f"Сервер вернул: {res.status_code}"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
        except Exception as e:
            Popup(title="Ошибка", content=Label(text=str(e)), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()

    def add_to_cart(self, instance):
        import main
        try:
            res = requests.post(f"{main.API_URL}/api/cart/add", json={"product_id": self.product_data['id'], "quantity": int(self.qty_label.text), "size": self.size_spinner.text}, headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            ok = res.status_code == 200
            Popup(title="Успех" if ok else "Ошибка", content=Label(text="Добавлено!" if ok else "Ошибка"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            if ok: self.manager.get_screen('main').update_cart_count()
        except Exception as e:
            pass

    def edit_product(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        content.add_widget(Label(text="Название:", size_hint_y=None, height=25))
        self.edit_name = TextInput(text=self.product_data.get('name', ''), multiline=False, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=(0,0,0,1), padding=(5, 5))
        content.add_widget(self.edit_name)
        content.add_widget(Label(text="Цена:", size_hint_y=None, height=25))
        self.edit_price = TextInput(text=str(self.product_data.get('price', 0)), multiline=False, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=(0,0,0,1), padding=(5, 5))
        content.add_widget(self.edit_price)
        content.add_widget(Label(text="Описание:", size_hint_y=None, height=25))
        self.edit_desc = TextInput(text=self.product_data.get('description', '') or '', multiline=True, size_hint_y=None, height=80, background_color=(1,1,1,1), foreground_color=(0,0,0,1), padding=(5, 5))
        content.add_widget(self.edit_desc)
        content.add_widget(Label(text="Наличие:", size_hint_y=None, height=25))
        self.edit_stock = Spinner(text='В наличии' if self.product_data.get('in_stock', True) else 'Нет', values=('В наличии', 'Нет'), background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), size_hint_y=None, height=40)
        content.add_widget(self.edit_stock)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_save = Button(text="Сохранить", background_color=PRIMARY, color=(1, 1, 1, 1))
        btn_save.bind(on_press=self.save_edit)
        btn_cancel = Button(text="Отмена", background_color=GRAY, color=(0,0,0,1))
        btn_cancel.bind(on_press=lambda x: self.edit_popup.dismiss())
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        self.edit_popup = Popup(title="Редактирование товара", content=content, size_hint=(0.9, 0.8), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1))
        self.edit_popup.open()

    def save_edit(self, instance):
        import main
        try:
            data = {"name": self.edit_name.text, "price": float(self.edit_price.text), "description": self.edit_desc.text, "in_stock": self.edit_stock.text == 'В наличии'}
            res = requests.put(f"{main.API_URL}/api/products/{self.product_data['id']}", json=data, headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            if res.status_code == 200:
                self.product_data.update(data)
                self.edit_popup.dismiss()
                self.render_product()
                Popup(title="Успех", content=Label(text="Обновлено!"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
        except Exception as e:
            pass

    def confirm_delete(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        content.add_widget(Label(text="Вы уверены, что хотите удалить\nэтот товар?", halign='center'))
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_yes = Button(text="Да, удалить", background_color=DANGER, color=(1,1,1,1))
        btn_yes.bind(on_press=self.delete_product)
        btn_no = Button(text="Отмена", background_color=GRAY, color=(0,0,0,1))
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        content.add_widget(btn_layout)
        self.delete_popup = Popup(title="Подтверждение", content=content, size_hint=(0.8, 0.4), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1))
        btn_no.bind(on_press=lambda x: self.delete_popup.dismiss())
        self.delete_popup.open()

    def delete_product(self, instance):
        import main
        self.delete_popup.dismiss()
        try:
            res = requests.delete(f"{main.API_URL}/api/products/{self.product_data['id']}", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            if res.status_code == 200:
                url = self.product_data.get('image_url')
                if url and url in self._image_cache:
                    del self._image_cache[url]
                Popup(title="Успех", content=Label(text="Удалено!"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 1)
        except Exception as e:
            pass