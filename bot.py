"""
Telegram-бот для генерации видео через ИИ.
"""

import logging
import threading
import time
import traceback
from typing import Dict

import telebot

import config
from request import generate_video


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class VideoBot:
    def __init__(self, token: str, api_key: str):
        if not token or "ваш" in token.lower():
            raise ValueError(
                "❌ ОШИБКА: BOT_TOKEN не найден. РЕШЕНИЕ: Создай бота через @BotFather и добавь токен в config.py/.env"
            )
        if not api_key or "ваш" in api_key.lower():
            raise ValueError(
                "❌ ОШИБКА: API_KEY не найден. РЕШЕНИЕ: Зарегистрируйся на proxyapi.ru и добавь ключ в config.py/.env"
            )
        self.bot = telebot.TeleBot(token, parse_mode="HTML")
        self.user_tasks: Dict[int, Dict] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self.bot.message_handler(commands=["start", "help"])
        def _welcome(message):
            self.send_welcome(message)

        @self.bot.message_handler(content_types=["text"])
        def _text(message):
            self.handle_message(message)

    @staticmethod
    def _progress_bar(progress: int, size: int = 20) -> str:
        filled = int(size * max(0, min(progress, 100)) / 100)
        return "🟩" * filled + "⬜" * (size - filled)

    def update_progress_message(self, user_id, message_id, status, progress, message_text):
        bar = self._progress_bar(progress)
        text = (
            f"🎬 <b>Генерация видео</b>\n"
            f"Статус: {status}\n"
            f"Прогресс: <code>{progress}%</code>\n"
            f"{bar}\n\n"
            f"{message_text}"
        )
        try:
            self.bot.edit_message_text(text, chat_id=user_id, message_id=message_id)
        except Exception:
            logger.debug("Не удалось обновить сообщение прогресса.")

    def generate_video_with_progress(self, prompt, user_id, message_id):
        try:
            self.user_tasks[user_id] = {"status": "in_progress", "prompt": prompt, "progress": 0}
            stages = [
                ("⏳ В очереди", 10, "Задача отправлена в API..."),
                ("🔄 Генерация", 45, "Видео создается, подожди немного..."),
                ("🔄 Генерация", 75, "Почти готово..."),
                ("📥 Скачивание", 90, "Скачиваю готовый файл..."),
            ]
            for status, prog, text in stages:
                self.update_progress_message(user_id, message_id, status, prog, text)
                time.sleep(2)

            video_path = generate_video(prompt)
            self.user_tasks[user_id] = {
                "status": "completed",
                "progress": 100,
                "video_path": video_path,
            }
            self.update_progress_message(user_id, message_id, "✅ Готово", 100, "Видео успешно создано!")

            with open(video_path, "rb") as f:
                self.bot.send_video(
                    user_id,
                    f,
                    caption="✅ УСПЕХ: Видео готово!",
                    supports_streaming=True,
                )
        except Exception as exc:
            error_text = str(exc)
            if "unexpected keyword argument 'proxies'" in error_text:
                error_text = (
                    "Конфликт версий openai/httpx. "
                    "Установи совместимую версию: pip install httpx==0.27.2 "
                    "или переустанови: pip install -r requirements.txt"
                )
            self.user_tasks[user_id] = {"status": "failed", "error": str(exc), "progress": 0}
            self.update_progress_message(
                user_id,
                message_id,
                "❌ Ошибка",
                0,
                f"❌ ОШИБКА: {error_text}\nРЕШЕНИЕ: Проверь API_KEY, баланс и подключение к интернету.",
            )
            logger.error("Ошибка генерации у пользователя %s: %s", user_id, exc)
            logger.debug("Traceback:\n%s", traceback.format_exc())

    def send_welcome(self, message):
        text = (
            "🤖 <b>Привет! Я VideoGeneratorAI-бот.</b>\n\n"
            "Отправь текстовый промпт, и я сгенерирую видео.\n"
            "Пример: <i>Кот в космосе, неоновый киберпанк, 4 секунды</i>"
        )
        self.bot.reply_to(message, text)

    def handle_message(self, message):
        user_id = message.chat.id
        prompt = message.text.strip()
        if not prompt:
            self.bot.reply_to(message, "⚠️ ПРЕДУПРЕЖДЕНИЕ: Пустой текст. Введи описание видео.")
            return
        if user_id in self.user_tasks and self.user_tasks[user_id].get("status") == "in_progress":
            self.bot.reply_to(message, "⚠️ Уже выполняется задача. Дождись завершения.")
            return
        progress_msg = self.bot.reply_to(message, "🎬 Запускаю генерацию...\n⏳ Подготовка...")
        thread = threading.Thread(
            target=self.generate_video_with_progress,
            args=(prompt, user_id, progress_msg.message_id),
            daemon=True,
        )
        thread.start()

    def start(self):
        logger.info("🚀 Запуск Telegram-бота...")
        logger.info("📋 Если бот не отвечает, проверь токен и polling.")
        self.bot.infinity_polling(timeout=60, long_polling_timeout=30)


if __name__ == "__main__":
    bot = VideoBot(config.BOT_TOKEN, config.API_KEY)
    bot.start()


# Пример использования:
# from bot import VideoBot
# from config import BOT_TOKEN, API_KEY
# bot = VideoBot(BOT_TOKEN, API_KEY)
# bot.start()
