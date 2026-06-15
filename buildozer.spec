[app]
title = Igor KITT
package.name = igorkitt
package.domain = org.vanadio.igorkitt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,httpx,pillow
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.1
fullscreen = 1
android.api = 34
android.minapi = 24
android.ndk = 27b
android.sdk = 34
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, RECORD_AUDIO
android.add_src =
android.gradle_depends =
android.accept_sdk_license = True
android.private_storage = True
android.wakelock = True
android.copy_libs = 1
android.google_play_keyboard = True
android.keyboard_mode = system
android.notch = True
android.entrypoint = main.py
presplash.color = #0a0a0f
icon = icon.png

[buildozer]
log_level = 2
warn_on_root = 1
