[app]
title = SportLife
package.name = sportlife
package.domain = ru.sportlife

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.0
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0
log_level = 2

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
