"""
Автоматическое исправление частых проблем проекта.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def ensure_generated_dir():
    path = ROOT / "generated_videos"
    if path.exists():
        print("✅ УСПЕХ: Папка generated_videos уже существует.")
    else:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Папка generated_videos не найдена.")
        print("🔧 ИСПРАВЛЯЮ: Создаю папку generated_videos...")
        path.mkdir(parents=True, exist_ok=True)
        print("✅ УСПЕХ: Папка успешно создана.")


def ensure_env():
    env = ROOT / ".env"
    env_example = ROOT / ".env.example"
    if env.exists():
        print("✅ УСПЕХ: .env уже существует.")
        return
    if env_example.exists():
        print("🔧 ИСПРАВЛЯЮ: Создаю .env из .env.example...")
        shutil.copy(env_example, env)
        print("✅ УСПЕХ: .env создан. Заполни API_KEY и BOT_TOKEN.")
    else:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: .env.example не найден, .env не создан.")


def install_requirements():
    req = ROOT / "requirements.txt"
    if not req.exists():
        print("❌ ОШИБКА: requirements.txt не найден.")
        return
    print("🔧 ИСПРАВЛЯЮ: Устанавливаю зависимости...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)
    if result.returncode == 0:
        print("✅ УСПЕХ: Зависимости установлены.")
    else:
        print("❌ ОШИБКА: Не удалось установить зависимости.")
        print("РЕШЕНИЕ: Выполни вручную: pip install -r requirements.txt")


def check_permissions():
    print("🔍 Проверка прав доступа к папкам...")
    for folder in [ROOT, ROOT / "generated_videos", ROOT / "templates", ROOT / "diagnostics"]:
        if not folder.exists():
            continue
        if os.access(folder, os.R_OK | os.W_OK):
            print(f"✅ УСПЕХ: Есть права на чтение/запись: {folder}")
        else:
            print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: Недостаточно прав: {folder}")


def main():
    ensure_generated_dir()
    ensure_env()
    install_requirements()
    check_permissions()
    print("📋 ИНФОРМАЦИЯ: Базовое исправление частых проблем завершено.")


if __name__ == "__main__":
    main()


# Пример использования:
# python diagnostics/fix_common_issues.py
