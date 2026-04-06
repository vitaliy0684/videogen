"""
Проверка зависимостей проекта.
"""

import importlib


REQUIRED = {
    "flask": ("Flask", "3.0"),
    "openai": ("openai", "1.30"),
    "telebot": ("pyTelegramBotAPI", "4.16"),
    "dotenv": ("python-dotenv", "1.0"),
    "requests": ("requests", "2.31"),
}


def main():
    print("[1/4] 🔍 Проверка зависимостей из requirements.txt...")
    missing = []
    for module_name, (package_name, min_version) in REQUIRED.items():
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ УСПЕХ: {package_name} найден (версия: {version})")
            if version != "unknown" and version < min_version:
                print(
                    f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {package_name} старой версии ({version}). "
                    f"Рекомендуется {min_version}+."
                )
        except Exception:
            missing.append(package_name)
            print(f"❌ ОШИБКА: {package_name} не найден.")

    print("[2/4] 🔍 Проверка завершена.")
    if missing:
        print(f"[3/4] ❌ Отсутствуют пакеты: {', '.join(missing)}")
        print("[4/4] 🔧 РЕШЕНИЕ: Выполни команду: pip install -r requirements.txt")
    else:
        print("[3/4] ✅ Все зависимости установлены.")
        print("[4/4] ✅ УСПЕХ: Окружение готово.")


if __name__ == "__main__":
    main()


# Пример использования:
# python diagnostics/check_dependencies.py
