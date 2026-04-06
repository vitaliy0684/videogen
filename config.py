"""
Конфигурация проекта VideoGeneratorAI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ключ Proxy API.
# Получить: https://proxyapi.ru
API_KEY = os.getenv("API_KEY", "")

# Токен Telegram-бота.
# Получить через @BotFather в Telegram.
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Модель для генерации видео.
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "sora-2")

# Длительность видео в секундах.
VIDEO_SECONDS = int(os.getenv("VIDEO_SECONDS", "4"))

# Базовый URL Proxy API.
PROXY_API_URL = os.getenv("PROXY_API_URL", "https://api.proxyapi.ru/openai/v1")

# Папка для сохранения видео.
GENERATED_VIDEOS_DIR = os.getenv("GENERATED_VIDEOS_DIR", "generated_videos")
GENERATED_VIDEOS_PATH = Path(GENERATED_VIDEOS_DIR)

# Режим отладки.
DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes", "on"}


# Пример использования:
# from config import API_KEY, BOT_TOKEN
# print(API_KEY, BOT_TOKEN)
