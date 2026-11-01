[app]
# Название приложения
title = SportLife
package.name = sportlife
package.domain = ru.sportlife

source.dir = .
# Какие файлы включить в сборку
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 1.0

# Зависимости. Добавлены requests и все нужное для работы с сетью
requirements = python3==3.10.12,kivy==2.3.0,hostpython3==3.10.12,pyjnius==1.5.0
orientation = portrait
fullscreen = 0
log_level = 2

# Разрешения для Android (Интернет обязателен для работы с API)
android.permissions = INTERNET, ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b

# Архитектуры процессоров (для современных и старых телефонов)
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
