@echo off
cd /d "S:\WorkShop\cursor\alpha\backend"
set DJANGO_SETTINGS_MODULE=alpha.settings
py manage.py runserver 127.0.0.1:8000
pause