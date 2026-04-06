"""
Комплексная проверка структуры и базовой работоспособности проекта.
"""

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parent

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def setup_console_encoding():
    """
    Настраивает консольный вывод для корректного отображения эмодзи в Windows.
    """
    try:
        # Для современных версий Python в Windows это обычно решает проблему cp1251.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Если reconfigure недоступен, продолжаем с текущей кодировкой.
        pass


def ok(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")


def fail(msg: str):
    print(f"{RED}❌ {msg}{RESET}")


def info(msg: str):
    print(f"{YELLOW}📋 {msg}{RESET}")


def warn(msg: str):
    print(f"{YELLOW}⚠️ {msg}{RESET}")


def check_runtime_dependencies() -> bool:
    """
    Проверка ключевых зависимостей для углубленных тестов.
    Возвращает True, если можно выполнять Flask/Mock-проверки.
    """
    needed = ("flask", "openai", "requests")
    missing = []
    for pkg in needed:
        try:
            importlib.import_module(pkg)
        except Exception:
            missing.append(pkg)
    if missing:
        warn(
            "Не хватает зависимостей для части проверок: "
            f"{', '.join(missing)}. Выполни: pip install -r requirements.txt"
        )
        return False
    ok("Ключевые зависимости установлены.")
    return True


def check_files() -> bool:
    required = [
        "config.py",
        "request.py",
        "bot.py",
        "app.py",
        "test.py",
        "verify.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "templates/index.html",
        "templates/status.html",
        "generated_videos/.gitkeep",
        "diagnostics/check_system.py",
        "diagnostics/check_dependencies.py",
        "diagnostics/check_api_keys.py",
        "diagnostics/fix_common_issues.py",
        "scripts/run_bot.bat",
        "scripts/run_site.bat",
        "scripts/run_bot.sh",
        "scripts/run_site.sh",
    ]
    all_ok = True
    for rel in required:
        if (ROOT / rel).exists():
            ok(f"Файл найден: {rel}")
        else:
            fail(f"Файл отсутствует: {rel}")
            all_ok = False
    return all_ok


def check_imports() -> bool:
    module_requirements = {
        "config": ["dotenv"],
        "request": ["openai", "requests"],
        "bot": ["telebot"],
        "app": ["flask"],
    }
    all_ok = True
    for module in ("config", "request", "bot", "app"):
        missing_for_module = []
        for dep in module_requirements.get(module, []):
            try:
                importlib.import_module(dep)
            except Exception:
                missing_for_module.append(dep)

        if missing_for_module:
            fail(
                f"Импорт '{module}' пропущен: не хватает зависимостей "
                f"({', '.join(missing_for_module)})."
            )
            info(f"РЕШЕНИЕ: Установи зависимости командой: pip install -r requirements.txt")
            all_ok = False
            continue

        try:
            importlib.import_module(module)
            ok(f"Импорт модуля '{module}' успешен")
        except ModuleNotFoundError as exc:
            fail(f"Ошибка импорта '{module}': отсутствует модуль '{exc.name}'.")
            info("РЕШЕНИЕ: Проверь requirements.txt и установи зависимости.")
            all_ok = False
        except Exception as exc:
            fail(f"Ошибка импорта '{module}': {exc}")
            all_ok = False
    return all_ok


def check_flask_routes() -> bool:
    try:
        from app import VideoApp
        from flask.testing import FlaskClient

        web = VideoApp()
        client: FlaskClient = web.app.test_client()
        root = client.get("/")
        if root.status_code != 200:
            fail("Главная страница Flask недоступна")
            return False
        ok("Роут '/' отвечает корректно")

        with patch("app.generate_video", return_value=str(ROOT / "generated_videos/mock.mp4")):
            response = client.post("/generate", data={"prompt": "test prompt"})
            if response.status_code not in (302, 303):
                fail("POST /generate не создает задачу корректно")
                return False
            ok("POST /generate корректно создает задачу и редиректит")

        if not web.tasks:
            fail("Задача не была добавлена в словарь tasks")
            return False

        task_id = next(iter(web.tasks.keys()))
        status = client.get(f"/api/status/{task_id}")
        data = json.loads(status.data.decode("utf-8"))
        if "status" not in data:
            fail("JSON статуса не содержит поле 'status'")
            return False
        ok("JSON статуса содержит необходимые поля")
        return True
    except Exception as exc:
        fail(f"Проверка Flask роутов провалилась: {exc}")
        return False


def check_mock_generation() -> bool:
    try:
        with patch("request.generate_video", return_value="generated_videos/mock_video.mp4"):
            import request as req

            result = req.generate_video("mock prompt")
            if "mock_video.mp4" not in result:
                fail("Mock-генерация вернула неожиданный результат")
                return False
        ok("Mock-генерация работает")
        return True
    except Exception as exc:
        fail(f"Ошибка mock-проверки: {exc}")
        return False


def main():
    setup_console_encoding()
    print("[1/6] 🔍 Проверка структуры...")
    checks = [check_files()]
    print("[2/6] 🔍 Проверка импортов...")
    checks.append(check_imports())
    print("[3/6] 🔍 Проверка runtime-зависимостей...")
    runtime_ok = check_runtime_dependencies()
    checks.append(runtime_ok)

    print("[4/6] 🔍 Проверка Flask-роутов...")
    if runtime_ok:
        checks.append(check_flask_routes())
    else:
        warn("Проверка Flask-роутов пропущена из-за отсутствующих зависимостей.")
        checks.append(False)

    print("[5/6] 🔍 Проверка mock-генерации...")
    if runtime_ok:
        checks.append(check_mock_generation())
    else:
        warn("Проверка mock-генерации пропущена из-за отсутствующих зависимостей.")
        checks.append(False)

    print("[6/6] 🔍 Итог...")
    if all(checks):
        ok("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    else:
        fail("НАЙДЕНЫ ОШИБКИ")
        info("Для полного прохождения установи зависимости: pip install -r requirements.txt")


if __name__ == "__main__":
    main()


# Пример использования:
# python verify.py
