# VideoGeneratorAI

Генератор видео через ИИ с двумя интерфейсами:
- 🤖 Telegram-бот
- 🌐 Flask-сайт

Проект использует Proxy API для генерации видео и сохраняет результаты в `generated_videos/`.

## Возможности

- Генерация видео по текстовому промпту
- Прогресс и статусы задач
- Отправка видео в Telegram
- Веб-интерфейс с формой, статусом и скачиванием
- Диагностические скрипты для системы, зависимостей и ключей
- Скрипты запуска для Windows и Linux/macOS

## Структура

Ключевые файлы:
- `bot.py` — Telegram-бот
- `app.py` — Flask-приложение
- `request.py` — логика генерации видео (SDK + HTTP fallback)
- `config.py` — конфигурация и переменные окружения
- `test.py` — проверка цепочки генерации
- `verify.py` — комплексная проверка проекта

## Требования

- Python 3.8+
- Установленные зависимости из `requirements.txt`
- API ключ Proxy API
- Telegram bot token (для бота)

## Установка

```bash
pip install -r requirements.txt
```

Если у тебя несколько версий Python, используй:

```bash
python -m pip install -r requirements.txt
```

## Настройка

Создай `.env` (можно из `.env.example`) и заполни:

```env
API_KEY=ваш_ключ_proxyapi
BOT_TOKEN=ваш_токен_telegram
VIDEO_MODEL=sora-2
VIDEO_SECONDS=4
```

## Запуск

### Telegram-бот

```bash
python bot.py
```

Windows-скрипт:

```powershell
scripts\run_bot.bat
```

### Flask-сайт

```bash
python app.py
```

Открой:
- [http://127.0.0.1:5000](http://127.0.0.1:5000)

Windows-скрипт:

```powershell
scripts\run_site.bat
```

## Проверки и диагностика

```bash
python verify.py
python diagnostics/check_system.py
python diagnostics/check_dependencies.py
python diagnostics/check_api_keys.py
```

Тест генерации:

```bash
python test.py --prompt "Кот в космосе" --test-api
```

## Частые проблемы

- `ModuleNotFoundError: telebot`
  - установи зависимости в том же интерпретаторе, которым запускаешь бот
- `Client.__init__() got an unexpected keyword argument 'proxies'`
  - в проекте зафиксирован `httpx==0.27.2`; переустанови зависимости
- Telegram 409 conflict
  - запущено несколько экземпляров бота, оставь только один процесс

Подробные инструкции смотри в `docs/`.

## Деплой на PythonAnywhere

Платформа: [PythonAnywhere](https://www.pythonanywhere.com/)

1. Создай аккаунт и открой **Bash Console**.
2. Клонируй репозиторий:
   ```bash
   git clone https://github.com/vitaliy0684/videogen.git
   cd videogen
   ```
3. Создай виртуальное окружение и установи зависимости:
   ```bash
   mkvirtualenv --python=python3.10 videogen-env
   pip install -r requirements.txt
   ```
4. Создай файл `.env` в корне проекта и заполни `API_KEY`, `BOT_TOKEN` (по необходимости).
5. Во вкладке **Web** создай новое Flask-приложение (Manual configuration, Python 3.10).
6. В `WSGI configuration file` укажи проект:
   ```python
   import sys
   path = '/home/<your_username>/videogen'
   if path not in sys.path:
       sys.path.append(path)

   from wsgi import application
   ```
7. В разделе **Virtualenv** укажи путь к окружению:
   - `/home/<your_username>/.virtualenvs/videogen-env`
8. Нажми **Reload** в разделе Web.

После перезагрузки сайт будет доступен по адресу:
- `https://<your_username>.pythonanywhere.com`
