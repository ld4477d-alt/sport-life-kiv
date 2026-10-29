from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
from style import *

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Спорт Лайф", font_size=32, bold=True, color=PRIMARY, size_hint_y=None, height=80))
        layout.add_widget(Label(text="Вход в аккаунт", font_size=18, color=TEXT_COLOR, size_hint_y=None, height=40))
        self.email = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=50, background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        self.password = TextInput(hint_text="Пароль", password=True, multiline=False, size_hint_y=None, height=50, background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        layout.add_widget(self.email); layout.add_widget(self.password)
        self.status_label = Label(text="", color=TEXT_COLOR, size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        btn_login = Button(text="Войти", size_hint_y=None, height=50, background_color=PRIMARY, color=(1,1,1,1), bold=True)
        btn_login.bind(on_press=self.do_login)
        layout.add_widget(btn_login)
        btn_register = Button(text="Создать аккаунт", size_hint_y=None, height=40, background_color=GRAY, color=TEXT_COLOR)
        btn_register.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(btn_register)
        btn_guest = Button(text="Войти как гость", size_hint_y=None, height=40, background_color=get_color_from_hex('#FFA726'), color=(1,1,1,1))
        btn_guest.bind(on_press=self.guest_login)
        layout.add_widget(btn_guest)
        self.add_widget(layout)

    def do_login(self, instance):
        import main
        if not self.email.text or not self.password.text:
            self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Заполните все поля"; return
        try:
            res = requests.post(f"{main.API_URL}/api/auth/login", json={"email": self.email.text, "password": self.password.text})
            if res.status_code == 200:
                data = res.json()
                main.CURRENT_TOKEN = data.get("access_token")
                headers = {"Authorization": f"Bearer {main.CURRENT_TOKEN}"}
                user_res = requests.get(f"{main.API_URL}/api/auth/me", headers=headers)
                if user_res.status_code == 200:
                    main.CURRENT_ROLE = user_res.json().get("role", "CUSTOMER")
                self.status_label.color = get_color_from_hex('#4CAF50'); self.status_label.text = "Успешный вход!"
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 1)
            else:
                self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Неверный email или пароль"
        except:
            self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Сервер недоступен"

    def guest_login(self, instance):
        import main
        main.CURRENT_TOKEN = None; main.CURRENT_ROLE = "GUEST"
        self.manager.current = 'main'
