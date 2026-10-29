from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from io import BytesIO
import requests, os
from style import *

class ProductCard(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 120
        self.padding = 10
        self.spacing = 10
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self._image_cache = {}

        # ================= ШАПКА =================
        top = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
        header = BoxLayout(size_hint_y=None, height=60, padding=(5, 10), spacing=5)
        
        # Название
        title_lbl = Label(text="КАТАЛОГ", font_size=20, bold=True, color=TEXT_COLOR, 
                          halign='left', valign='middle', size_hint_x=None, width=110)
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        header.add_widget(title_lbl)

        # Кнопки справа (Люди, Избранное, Корзина, Профиль/Выход)
        # Для админа
        self.btn_users = Button(text="Люди", font_size=11, size_hint_x=None, width=60,
                                background_color=WARNING, color=(1, 1, 1, 1), bold=True)
        self.btn_users.bind(on_press=lambda x: setattr(self.manager, 'current', 'users'))
        header.add_widget(self.btn_users)

        # Для покупателя
        self.btn_fav = Button(text="Избранное", font_size=10, size_hint_x=None, width=80,
                              background_color=GRAY, color=PRIMARY, bold=True)
        self.btn_fav.bind(on_press=lambda x: setattr(self.manager, 'current', 'favorites'))
        header.add_widget(self.btn_fav)

        self.btn_cart = Button(text="Корзина", font_size=10, size_hint_x=None, width=75,
                               background_color=PRIMARY, color=(1, 1, 1, 1))
        self.btn_cart.bind(on_press=self.open_cart)
        header.add_widget(self.btn_cart)

        self.btn_profile_or_logout = Button(text="Выход", font_size=10, size_hint_x=None, width=65,
                                  background_color=DANGER, color=(1, 1, 1, 1))
        self.btn_profile_or_logout.bind(on_press=self.on_profile_or_logout_press)
        header.add_widget(self.btn_profile_or_logout)

        top.add_widget(header)

        search_layout = BoxLayout(size_hint_y=None, height=45, padding=(10, 0))
        self.search_input = TextInput(hint_text="Поиск...", multiline=False,
                                      background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        self.search_input.bind(text=self.on_search)
        search_layout.add_widget(self.search_input)
        top.add_widget(search_layout)

        filters = BoxLayout(size_hint_y=None, height=40, spacing=5, padding=(10, 0))
        self.cat_btn = Button(text="Все", background_color=PRIMARY, color=(1, 1, 1, 1))
        self.cat_btn.bind(on_release=self.show_cat_menu)
        filters.add_widget(self.cat_btn)
        top.add_widget(filters)
        self.layout.add_widget(top)

        # ================= СПИСОК ТОВАРОВ =================
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.products_list = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.products_list.bind(minimum_height=self.products_list.setter('height'))
        self.scroll.add_widget(self.products_list)
        self.layout.add_widget(self.scroll)

        # ================= КНОПКА ДОБАВЛЕНИЯ (Админ) =================
        self.btn_add = Button(text="+ Добавить товар", size_hint_y=None, height=50,
                              background_color=PRIMARY, color=(1, 1, 1, 1), bold=True)
        self.btn_add.bind(on_press=self.open_add_popup)
        self.add_widget(self.layout)

        self.all_products = []
        self.selected_image_path = ""

    def on_profile_or_logout_press(self, instance):
        import main
        if main.CURRENT_ROLE == "ADMIN":
            self.logout(instance)
        else:
            self.manager.current = 'profile'

    def on_enter(self):
        import main
        if main.CURRENT_ROLE == "ADMIN":
            if self.btn_add not in self.layout.children:
                self.layout.add_widget(self.btn_add)
            self.btn_cart.disabled = True
            self.btn_cart.opacity = 0
            self.btn_fav.disabled = True
            self.btn_fav.opacity = 0
            self.btn_users.disabled = False
            self.btn_users.opacity = 1
            self.btn_profile_or_logout.text = "Выход"
            self.btn_profile_or_logout.background_color = get_color_from_hex('#EF5350')
        else:
            if self.btn_add in self.layout.children:
                self.layout.remove_widget(self.btn_add)
            self.btn_cart.disabled = False
            self.btn_cart.opacity = 1
            self.btn_fav.disabled = False
            self.btn_fav.opacity = 1
            self.btn_users.disabled = True
            self.btn_users.opacity = 0
            self.btn_profile_or_logout.text = "Профиль"
            self.btn_profile_or_logout.background_color = get_color_from_hex('#FFA726')
        self.load_products()
        if main.CURRENT_ROLE == "CUSTOMER":
            self.update_cart_count()

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
            response = requests.get(url, timeout=3)
            if response.status_code != 200:
                return None
            ext = self._detect_ext(url, response.headers.get("Content-Type", ""))
            core_img = CoreImage(BytesIO(response.content), ext=ext)
            self._image_cache[url] = core_img
            return core_img.texture
        except Exception as e:
            return None

    def update_cart_count(self):
        import main
        if main.CURRENT_ROLE != "CUSTOMER": return
        try:
            res = requests.get(f"{main.API_URL}/api/cart", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            if res.status_code == 200:
                main.CART_COUNT = len(res.json())
                self.btn_cart.text = f"Корзина ({main.CART_COUNT})"
        except: pass

    def show_cat_menu(self, btn):
        from kivy.uix.dropdown import DropDown
        dropdown = DropDown()
        for cat in ["Все", "Обувь", "Одежда"]:
            b = Button(text=cat, size_hint_y=None, height=40, background_color=GRAY, color=TEXT_COLOR)
            b.bind(on_release=lambda x, c=cat: self.set_cat(c, dropdown))
            dropdown.add_widget(b)
        dropdown.open(btn)

    def set_cat(self, cat, dropdown):
        self.cat_btn.text = cat
        dropdown.dismiss()
        self.apply_filters()

    def load_products(self):
        import main
        try:
            res = requests.get(f"{main.API_URL}/api/products")
            if res.status_code == 200:
                self.all_products = res.json()
                self.apply_filters()
        except Exception as e:
            print(f"Ошибка: {e}")

    def on_search(self, instance, value):
        self.apply_filters()

    def apply_filters(self):
        search_text = self.search_input.text.lower()
        cat_text = self.cat_btn.text
        filtered = []
        for p in self.all_products:
            if not p.get('name') or not p.get('price'):
                continue
            if search_text and search_text not in str(p['name']).lower():
                continue
            if cat_text not in ["Все", "Все категории"]:
                cid = 1 if cat_text == "Обувь" else 2
                if p.get('category_id') != cid:
                    continue
            filtered.append(p)
        self.render_products(filtered)

    def render_products(self, products):
        self.products_list.clear_widgets()
        if not products:
            lbl = Label(text="Нет товаров", color=TEXT_COLOR, font_size=18, size_hint_y=None, height=50)
            self.products_list.add_widget(lbl)
            self._force_layout_update()
            return
        
        for idx, p in enumerate(products):
            card = self.create_product_card(p, idx)
            self.products_list.add_widget(card)
        
        self._force_layout_update()

    def _force_layout_update(self):
        def update_once(dt):
            self.products_list.do_layout()
            self.scroll.scroll_y = 1.0
        Clock.schedule_once(update_once, 0.05)
        Clock.schedule_once(update_once, 0.2)

    def create_product_card(self, p, idx):
        img_url = str(p.get('image_url', '')).strip()
        card = ProductCard()
        card.bind(on_release=lambda x, prod=p: self.open_product(prod))
        
        texture = self._get_texture(img_url)
        if texture:
            img_widget = Image(texture=texture, size_hint=(None, 1), width=100, allow_stretch=True, keep_ratio=True)
        else:
            img_widget = Label(text="Нет фото", size_hint=(None, 1), width=100, color=get_color_from_hex('#757575'))
        
        center = BoxLayout(orientation='vertical', size_hint_x=1, padding=(5, 0))
        brand = p.get('brand', '') or 'Без бренда'
        brand_lbl = Label(text=brand, font_size=12, color=get_color_from_hex('#757575'), size_hint_y=None, height=20, halign='center')
        brand_lbl.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        name_lbl = Label(text=str(p['name']), bold=True, color=(0, 0, 0, 1), font_size=16, size_hint_y=None, height=30, halign='center')
        name_lbl.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        center.add_widget(brand_lbl)
        center.add_widget(name_lbl)
        
        try:
            price = float(p['price'])
            price_text = f"{price:.0f} ₽"
        except:
            price_text = "Цена?"
        price_lbl = Label(text=price_text, color=(0.1, 0.46, 0.82, 1), font_size=16, bold=True, size_hint_x=None, width=110, halign='right')
        price_lbl.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        card.add_widget(img_widget)
        card.add_widget(center)
        card.add_widget(price_lbl)
        return card

    def open_product(self, p):
        self.manager.get_screen('product').set_product(p)
        self.manager.current = 'product'

    def open_cart(self, instance):
        self.manager.get_screen('cart').load_cart()
        self.manager.current = 'cart'

    def open_add_popup(self, instance):
        # ... (остается без изменений)
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Название:", size_hint_y=None, height=20))
        self.new_name = TextInput(hint_text="Название", multiline=False, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=(0,0,0,1), padding=(5, 5))
        content.add_widget(Label(text="Цена:", size_hint_y=None, height=20))
        self.new_price = TextInput(hint_text="Цена", multiline=False, size_hint_y=None, height=40, background_color=(1,1,1,1), foreground_color=(0,0,0,1), padding=(5, 5))
        self.image_label = Label(text="Фото не выбрано", color=(0,0,0,1), size_hint_y=None, height=30) 
        btn_choose = Button(text="Выбрать фото", size_hint_y=None, height=40, background_color=PRIMARY, color=(1, 1, 1, 1))
        btn_choose.bind(on_press=self.choose_image)
        
        content.add_widget(self.new_name)
        content.add_widget(self.new_price)
        content.add_widget(self.image_label)
        content.add_widget(btn_choose)
        
        self.cat_spinner = Spinner(text='Обувь', values=('Обувь', 'Одежда'), background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), size_hint_y=None, height=40)
        self.brand_spinner = Spinner(text='Nike', values=('Nike', 'Adidas', 'Puma'), background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), size_hint_y=None, height=40)
        self.color_spinner = Spinner(text='Черный', values=('Черный', 'Белый', 'Красный', 'Синий', 'Серый'), background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), size_hint_y=None, height=40)
        content.add_widget(self.cat_spinner)
        content.add_widget(self.brand_spinner)
        content.add_widget(self.color_spinner)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_save = Button(text="Сохранить", background_color=PRIMARY, color=(1, 1, 1, 1))
        btn_save.bind(on_press=self.save_new_product)
        btn_cancel = Button(text="Отмена", background_color=GRAY, color=(0,0,0,1))
        btn_cancel.bind(on_press=lambda x: self.popup.dismiss())
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        self.popup = Popup(title="Новый товар", content=content, size_hint=(0.9, 0.8), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1))
        self.popup.open()

    def choose_image(self, instance):
        # ... (остается без изменений)
        chooser = FileChooserListView(path=os.path.expanduser("~"), filters=['*.png', '*.jpg', '*.jpeg'])
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_select = Button(text="Выбрать", background_color=PRIMARY, color=(1, 1, 1, 1))
        btn_close = Button(text="Отмена", background_color=GRAY, color=(0,0,0,1))

        def select_file(inst):
            if chooser.selection:
                self.selected_image_path = chooser.selection[0]
                self.image_label.text = f"Выбрано: {os.path.basename(self.selected_image_path)}"
                self.image_label.color = get_color_from_hex('#4CAF50')
                file_popup.dismiss()

        btn_select.bind(on_press=select_file)
        btn_close.bind(on_press=lambda x: file_popup.dismiss())
        btn_layout.add_widget(btn_select)
        btn_layout.add_widget(btn_close)
        layout.add_widget(btn_layout)

        file_popup = Popup(title="Выберите фото", content=layout, size_hint=(0.9, 0.9), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1))
        file_popup.open()

    def save_new_product(self, instance):
        # ... (остается без изменений)
        import main
        if not self.new_name.text or not self.new_price.text:
            Popup(title="Ошибка", content=Label(text="Заполните название и цену"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            return
        try:
            price_float = float(self.new_price.text)
        except ValueError:
            Popup(title="Ошибка", content=Label(text="Цена должна быть числом!"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
            return
        try:
            headers = {"Authorization": f"Bearer {main.CURRENT_TOKEN}"}
            image_url = ""
            if self.selected_image_path:
                with open(self.selected_image_path, 'rb') as f:
                    files = {'file': (os.path.basename(self.selected_image_path), f.read(), 'image/jpeg')}
                    upload_res = requests.post(f"{main.API_URL}/api/products/upload", files=files)
                    if upload_res.status_code == 200:
                        image_url = upload_res.json().get("url")

            requests.post(f"{main.API_URL}/api/products/categories?name={self.cat_spinner.text}")
            cid = 1 if self.cat_spinner.text == "Обувь" else 2
            data = {
                "name": self.new_name.text.strip(), "description": "", "price": price_float,
                "category_id": cid, "brand": self.brand_spinner.text, "image_url": image_url, "color": self.color_spinner.text
            }
            res = requests.post(f"{main.API_URL}/api/products", json=data, headers=headers)
            if res.status_code == 200:
                self.popup.dismiss()
                self.selected_image_path = ""
                self.new_name.text = ""
                self.new_price.text = ""
                self.image_label.text = "Фото не выбрано"
                self.image_label.color = (0,0,0,1)
                self.load_products()
            else:
                Popup(title="Ошибка", content=Label(text=f"Код: {res.status_code}"), size_hint=(0.7, 0.3), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()
        except Exception as e:
            Popup(title="Ошибка", content=Label(text=str(e)), size_hint=(0.8, 0.4), background_color=(0.95, 0.95, 0.95, 1), title_color=(0,0,0,1)).open()

    def logout(self, instance):
        import main
        main.CURRENT_TOKEN = None
        main.CURRENT_ROLE = "GUEST"
        main.CURRENT_USER_ID = None
        self.manager.current = 'login'