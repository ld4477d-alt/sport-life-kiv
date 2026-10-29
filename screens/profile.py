from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import requests
from style import *

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

    def on_enter(self): self.load_profile()

    def load_profile(self):
        import main
        self.layout.clear_widgets()
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        header.add_widget(Label(text="ПРОФИЛЬ", font_size=22, bold=True, color=TEXT_COLOR))
        
        btn_catalog = Button(text="Каталог", size_hint_x=None, width=120, background_color=PRIMARY, color=(1,1,1,1))
        btn_catalog.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header.add_widget(btn_catalog)
        self.layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        if main.CURRENT_ROLE == "GUEST" or not main.CURRENT_TOKEN:
            content.add_widget(Label(text="Вы вошли как гость", font_size=20, color=TEXT_COLOR, size_hint_y=None, height=40))
            btn_login = Button(text="Войти", size_hint_y=None, height=50, background_color=PRIMARY, color=(1,1,1,1), bold=True)
            btn_login.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
            content.add_widget(btn_login)
        else:
            try:
                res = requests.get(f"{main.API_URL}/api/auth/me", headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
                if res.status_code == 200:
                    u = res.json()
                    content.add_widget(Label(text="👤", font_size=80, color=PRIMARY, size_hint_y=None, height=120))
                    content.add_widget(Label(text=u.get('full_name', 'Пользователь'), font_size=24, bold=True, color=TEXT_COLOR, size_hint_y=None, height=40))
                    content.add_widget(Label(text=u.get('email', ''), font_size=16, color=WARNING, size_hint_y=None, height=30))
                    role_text = "Администратор" if main.CURRENT_ROLE == "ADMIN" else "Покупатель"
                    content.add_widget(Label(text=f"Роль: {role_text}", font_size=14, color=PRIMARY, size_hint_y=None, height=30))
                    
                    if main.CURRENT_ROLE == "CUSTOMER":
                        btn_orders = Button(text="Мои заказы", size_hint_y=None, height=50, background_color=GRAY, color=TEXT_COLOR)
                        btn_orders.bind(on_press=lambda x: setattr(self.manager, 'current', 'orders'))
                        content.add_widget(btn_orders)
                        
                        btn_fav = Button(text="Избранное", size_hint_y=None, height=50, background_color=GRAY, color=TEXT_COLOR)
                        btn_fav.bind(on_press=lambda x: setattr(self.manager, 'current', 'favorites'))
                        content.add_widget(btn_fav)
                    
                    btn_logout = Button(text="Выйти", size_hint_y=None, height=50, background_color=DANGER, color=(1,1,1,1))
                    btn_logout.bind(on_press=self.logout)
                    content.add_widget(btn_logout)
            except Exception as e:
                content.add_widget(Label(text=f"Ошибка загрузки: {e}", color=ERROR))

        scroll.add_widget(content)
        self.layout.add_widget(scroll)

    def logout(self, instance):
        import main
        main.CURRENT_TOKEN = None
        main.CURRENT_ROLE = "GUEST"
        main.CURRENT_USER_ID = None
        self.manager.current = 'login'