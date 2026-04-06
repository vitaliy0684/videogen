"""
Скрипт проверки полной цепочки генерации видео.
"""

import argparse
import traceback

from openai import OpenAI

import config
from request import generate_video


def check_config() -> bool:
    print("[1/4] 🔍 Проверка config.py и ключей...")
    if not config.API_KEY or "ваш" in config.API_KEY.lower():
        print(
            "❌ ОШИБКА: API_KEY не найден в config.py/.env. "
            "РЕШЕНИЕ: Зарегистрируйся на proxyapi.ru и вставь ключ."
        )
        return False
    print("✅ УСПЕХ: API_KEY найден.")
    return True


def test_api_connection() -> bool:
    print("[2/4] 🔍 Проверка подключения к Proxy API...")
    try:
        client = OpenAI(api_key=config.API_KEY, base_url=config.PROXY_API_URL)
        _ = client.models.list()
        print("✅ УСПЕХ: Подключение к Proxy API работает.")
        return True
    except Exception as exc:
        print(f"❌ ОШИБКА: Не удалось подключиться к API: {exc}")
        print("РЕШЕНИЕ: Проверь интернет, ключ API и баланс аккаунта.")
        return False


def test_video_generation(prompt: str) -> bool:
    print("[3/4] 🎬 Тест генерации видео...")
    try:
        file_path = generate_video(prompt)
        print(f"✅ УСПЕХ: Видео создано: {file_path}")
        return True
    except Exception as exc:
        print(f"❌ ОШИБКА: Генерация не удалась: {exc}")
        print("РЕШЕНИЕ: Проверь баланс API, модель sora-2 и корректность промпта.")
        print(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description="Тест проекта VideoGeneratorAI")
    parser.add_argument("--prompt", default="Короткое видео: кот машет лапой на фоне заката")
    parser.add_argument("--test-api", action="store_true", help="Проверить API до генерации")
    args = parser.parse_args()

    if not check_config():
        return

    if args.test_api and not test_api_connection():
        return

    print("[4/4] 🚀 Запуск финального теста...")
    ok = test_video_generation(args.prompt)
    if ok:
        print("✅ УСПЕХ: Все этапы теста завершены.")
    else:
        print("❌ ОШИБКА: Тест завершился с ошибкой. Смотри сообщения выше.")


if __name__ == "__main__":
    main()


# Пример использования:
# python test.py --prompt "Кот в космосе" --test-api
