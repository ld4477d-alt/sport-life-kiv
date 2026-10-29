from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import requests
from style import *


class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

    def on_enter(self):
        self.load_users()

    def load_users(self):
        import main
        self.layout.clear_widgets()

        # --- Шапка ---
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10))
        btn_back = Button(text="< Назад", size_hint_x=None, width=100,
                          background_color=BG_COLOR, color=PRIMARY, bold=True)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="ПОЛЬЗОВАТЕЛИ", font_size=20, bold=True, color=TEXT_COLOR))
        self.layout.add_widget(header)

        # --- Скролл ---
        scroll = ScrollView(size_hint=(1, 1))
        # Заменили BoxLayout на GridLayout (cols=1) — он стабильнее работает на Windows
        content = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Убираем невидимую заглушку, она здесь не нужна
        
        try:
            res = requests.get(f"{main.API_URL}/api/users",
                               headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            users = res.json() if res.status_code == 200 else []

            if not users:
                content.add_widget(Label(text="Нет пользователей", color=TEXT_COLOR,
                                         size_hint_y=None, height=100))
            else:
                for u in users:
                    # Карточка пользователя: жесткая высота 70, чтобы не растягивалась
                    card = BoxLayout(size_hint_y=None, height=70, padding=10, spacing=10)
                    
                    with card.canvas.before:
                        Color(0.95, 0.95, 0.95, 1)
                        card.rect = Rectangle(pos=card.pos, size=card.size)
                    card.bind(pos=lambda inst, val: setattr(card.rect, 'pos', val),
                              size=lambda inst, val: setattr(card.rect, 'size', val))

                    # Информация о пользователе
                    info = BoxLayout(orientation='vertical')
                    info.add_widget(Label(text=u.get('full_name', ''), bold=True, color=TEXT_COLOR))
                    info.add_widget(Label(text=u.get('email', ''), font_size=12,
                                          color=get_color_from_hex('#757575')))
                    card.add_widget(info)

                    # Выбор роли
                    role_spinner = Spinner(
                        text=u.get('role', 'CUSTOMER'),
                        values=('ADMIN', 'CUSTOMER'),
                        size_hint_x=None, width=110,
                        background_color=GRAY, color=TEXT_COLOR,
                        font_size=12
                    )
                    role_spinner.bind(on_text=lambda inst, val, user_id=u['id']: self.change_role(user_id, val))
                    card.add_widget(role_spinner)

                    # Кнопка удаления (только для других пользователей)
                    if u['id'] != main.CURRENT_USER_ID:
                        btn_del = Button(text="Удалить", size_hint_x=None, width=80,
                                         background_color=DANGER, color=(1, 1, 1, 1), font_size=12)
                        btn_del.bind(on_press=lambda x, user_id=u['id']: self.delete_user(user_id))
                        card.add_widget(btn_del)

                    content.add_widget(card)
        except Exception as e:
            content.add_widget(Label(text=f"Ошибка: {e}", color=ERROR,
                                     size_hint_y=None, height=100))

        scroll.add_widget(content)
        self.layout.add_widget(scroll)

        # Принудительная прокрутка вверх (если вдруг съедет)
        Clock.schedule_once(lambda dt: setattr(scroll, 'scroll_y', 1.0), 0.1)

    def change_role(self, user_id, new_role):
        import main
        try:
            requests.put(f"{main.API_URL}/api/users/{user_id}/role",
                         json={"role": new_role},
                         headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
        except:
            pass

    def delete_user(self, user_id):
        import main
        try:
            requests.delete(f"{main.API_URL}/api/users/{user_id}",
                            headers={"Authorization": f"Bearer {main.CURRENT_TOKEN}"})
            self.load_users()
        except:
            pass