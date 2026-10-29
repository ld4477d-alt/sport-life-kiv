[app]
title = Sport Life
package.name = sportlife
package.domain = org.sportlife

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
source.include_patterns = screens/*.py

version = 0.1

requirements = python3,kivy,requests,pyjnius

orientation = portrait
fullscreen = 1

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
