"""
Проверка системных требований.
"""

import os
import platform
import shutil
import socket
import sys


def check_python() -> bool:
    print("[1/4] 🔍 Проверка Python...")
    if sys.version_info < (3, 8):
        print("❌ ОШИБКА: Python слишком старый. РЕШЕНИЕ: Установи Python 3.8+.")
        return False
    print(f"✅ УСПЕХ: Найден Python {platform.python_version()}")
    return True


def check_os() -> bool:
    print("[2/4] 🔍 Проверка ОС...")
    print(f"📋 ИНФОРМАЦИЯ: Операционная система: {platform.system()} {platform.release()}")
    return True


def check_internet() -> bool:
    print("[3/4] 🔍 Проверка интернета...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3).close()
        print("✅ УСПЕХ: Интернет доступен.")
        return True
    except OSError:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Интернет недоступен. API-запросы могут не работать.")
        return False


def check_disk_space() -> bool:
    print("[4/4] 🔍 Проверка дискового пространства...")
    free = shutil.disk_usage(os.getcwd()).free
    free_gb = free / (1024**3)
    if free_gb < 1:
        print("❌ ОШИБКА: Мало места на диске (<1GB). РЕШЕНИЕ: Освободи минимум 1GB.")
        return False
    print(f"✅ УСПЕХ: Свободно {free_gb:.2f} GB.")
    return True


def main():
    checks = [check_python(), check_os(), check_internet(), check_disk_space()]
    if all(checks):
        print("✅ УСПЕХ: Система готова к запуску VideoGeneratorAI.")
    else:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Обнаружены проблемы, исправь их перед запуском.")


if __name__ == "__main__":
    main()


# Пример использования:
# python diagnostics/check_system.py
