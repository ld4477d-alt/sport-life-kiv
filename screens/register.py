from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
from style import *

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Регистрация", font_size=24, bold=True, color=PRIMARY, size_hint_y=None, height=60))
        self.full_name = TextInput(hint_text="ФИО", multiline=False, size_hint_y=None, height=50, background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        self.email = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=50, background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        self.password = TextInput(hint_text="Пароль (мин. 6 символов)", password=True, multiline=False, size_hint_y=None, height=50, background_color=GRAY, foreground_color=TEXT_COLOR, padding=(10, 10))
        layout.add_widget(self.full_name); layout.add_widget(self.email); layout.add_widget(self.password)
        self.status_label = Label(text="", color=TEXT_COLOR, size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        btn = Button(text="Создать аккаунт", size_hint_y=None, height=50, background_color=PRIMARY, color=(1,1,1,1), bold=True)
        btn.bind(on_press=self.do_register)
        layout.add_widget(btn)
        btn_back = Button(text="Назад", size_hint_y=None, height=40, background_color=GRAY, color=TEXT_COLOR)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def do_register(self, instance):
        import main
        if "@" not in self.email.text:
            self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Введите корректный Email"; return
        try:
            res = requests.post(f"{main.API_URL}/api/auth/register", json={"email": self.email.text, "password": self.password.text, "full_name": self.full_name.text})
            if res.status_code == 200:
                self.status_label.color = get_color_from_hex('#4CAF50'); self.status_label.text = "Успешно! Войдите."
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 2)
            else:
                self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Email уже занят"
        except:
            self.status_label.color = get_color_from_hex('#E53935'); self.status_label.text = "Сервер недоступен"
