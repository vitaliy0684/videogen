"""
WSGI entrypoint для деплоя на PythonAnywhere.
"""

from app import VideoApp

# PythonAnywhere ожидает переменную `application`.
application = VideoApp().app


# Пример использования:
# from wsgi import application
