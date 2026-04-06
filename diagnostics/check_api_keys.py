"""
Проверка API-ключей и токена бота.
"""

from pathlib import Path

from openai import OpenAI

import config


def main():
    print("[1/4] 🔍 Проверка наличия config.py...")
    if not Path("config.py").exists():
        print("❌ ОШИБКА: config.py не найден. РЕШЕНИЕ: Создай config.py или используй .env.")
        return
    print("✅ УСПЕХ: config.py найден.")

    print("[2/4] 🔍 Проверка API_KEY...")
    if not config.API_KEY or "ваш" in config.API_KEY.lower():
        print(
            "❌ ОШИБКА: API_KEY отсутствует. РЕШЕНИЕ: Зарегистрируйся на proxyapi.ru, "
            "получи ключ и добавь его в config.py/.env"
        )
        return
    print("✅ УСПЕХ: API_KEY заполнен.")

    print("[3/4] 🔍 Проверка BOT_TOKEN...")
    if not config.BOT_TOKEN or "ваш" in config.BOT_TOKEN.lower():
        print(
            "❌ ОШИБКА: BOT_TOKEN отсутствует. РЕШЕНИЕ: Напиши @BotFather, "
            "выполни /newbot и добавь токен в config.py/.env"
        )
        return
    print("✅ УСПЕХ: BOT_TOKEN заполнен.")

    print("[4/4] 🔍 Опциональная проверка API...")
    try:
        client = OpenAI(api_key=config.API_KEY, base_url=config.PROXY_API_URL)
        _ = client.models.list()
        print("✅ УСПЕХ: Тестовый запрос к API выполнен.")
    except Exception as exc:
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: API запрос не удался: {exc}")
        print("📋 ИНФОРМАЦИЯ: Возможно, проблема в сети, балансе или ограничениях аккаунта.")


if __name__ == "__main__":
    main()


# Пример использования:
# python diagnostics/check_api_keys.py
