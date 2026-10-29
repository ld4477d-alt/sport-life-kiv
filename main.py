from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform
from style import BG_COLOR
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.catalog import MainScreen
from screens.product import ProductScreen
from screens.cart import CartScreen
from screens.profile import ProfileScreen
from screens.favorites import FavoritesScreen
from screens.orders import OrdersScreen
from screens.users import UsersScreen

# ==========================================
# НАСТРОЙКА API ДЛЯ ТЕЛЕФОНА
# ==========================================
# Если запускаем на компьютере (Windows/Linux) - используем localhost
# Если на телефоне (Android) - используем IP-адрес компьютера в сети
if platform == 'android':
    API_URL = "http://192.168.3.75:8000"  # <-- ТВОЙ IP-АДРЕС
else:
    API_URL = "http://127.0.0.1:8000"

Window.size = (360, 640)
CURRENT_TOKEN = None
CURRENT_ROLE = "GUEST"
CURRENT_USER_ID = None
CART_COUNT = 0

class SportLifeApp(App):
    def build(self):
        Window.clearcolor = BG_COLOR
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ProductScreen(name='product'))
        sm.add_widget(CartScreen(name='cart'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(FavoritesScreen(name='favorites'))
        sm.add_widget(OrdersScreen(name='orders'))
        sm.add_widget(UsersScreen(name='users'))
        return sm

if __name__ == '__main__':
    SportLifeApp().run()
