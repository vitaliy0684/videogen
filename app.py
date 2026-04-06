"""
Flask-сайт для генерации видео через ИИ.
"""

import logging
import threading
import traceback
import uuid
from datetime import datetime, timedelta

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

import config
from request import generate_video


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class VideoApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.tasks = {}
        config.GENERATED_VIDEOS_PATH.mkdir(parents=True, exist_ok=True)
        self._setup_routes()

    def _cleanup_old_tasks(self) -> None:
        now = datetime.now()
        to_delete = []
        for task_id, task in self.tasks.items():
            if now - task["created_at"] > timedelta(hours=1):
                to_delete.append(task_id)
        for task_id in to_delete:
            self.tasks.pop(task_id, None)
            logger.info("🧹 Удалена старая задача: %s", task_id)

    def run_generation(self, task_id, prompt):
        try:
            self.tasks[task_id].update(status="in_progress", progress=20, message="🔄 Генерация началась...")
            video_path = generate_video(prompt)
            self.tasks[task_id].update(
                status="completed",
                progress=100,
                message="✅ Видео готово!",
                video_path=video_path,
            )
        except Exception as exc:
            self.tasks[task_id].update(
                status="failed",
                progress=0,
                message=f"❌ ОШИБКА: {exc}. РЕШЕНИЕ: Проверь ключ API, интернет и баланс.",
                error=str(exc),
            )
            logger.error("Ошибка фоновой генерации %s: %s", task_id, exc)
            logger.debug("Traceback:\n%s", traceback.format_exc())

    def index(self):
        self._cleanup_old_tasks()
        return render_template("index.html")

    def generate(self):
        prompt = (request.form.get("prompt") or "").strip()
        if not prompt:
            return jsonify(
                {"ok": False, "error": "❌ ОШИБКА: Пустой промпт. РЕШЕНИЕ: Введи описание видео."}
            ), 400

        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "queued",
            "progress": 5,
            "prompt": prompt,
            "message": "⏳ Задача поставлена в очередь...",
            "created_at": datetime.now(),
            "video_path": None,
        }
        thread = threading.Thread(target=self.run_generation, args=(task_id, prompt), daemon=True)
        thread.start()
        return redirect(url_for("status_page", task_id=task_id))

    def get_status(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            return jsonify(
                {"status": "failed", "message": "❌ ОШИБКА: Задача не найдена. РЕШЕНИЕ: Запусти генерацию заново."}
            ), 404
        return jsonify(
            {
                "status": task["status"],
                "progress": task.get("progress", 0),
                "message": task.get("message", ""),
                "download_url": url_for("download_video", task_id=task_id)
                if task.get("status") == "completed"
                else None,
            }
        )

    def status_page(self, task_id):
        if task_id not in self.tasks:
            return "❌ ОШИБКА: Задача не найдена.", 404
        return render_template("status.html", task_id=task_id)

    def download_video(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            return "❌ ОШИБКА: Задача не найдена.", 404
        video_path = task.get("video_path")
        if not video_path:
            return "⚠️ ПРЕДУПРЕЖДЕНИЕ: Видео еще не готово.", 400
        return send_file(video_path, as_attachment=True)

    def _setup_routes(self):
        self.app.add_url_rule("/", view_func=self.index, methods=["GET"])
        self.app.add_url_rule("/generate", view_func=self.generate, methods=["POST"])
        self.app.add_url_rule("/status/<task_id>", view_func=self.status_page, methods=["GET"])
        self.app.add_url_rule("/api/status/<task_id>", view_func=self.get_status, methods=["GET"])
        self.app.add_url_rule("/download/<task_id>", view_func=self.download_video, methods=["GET"])

    def run(self):
        logger.info("🌐 Веб-сайт запускается на http://0.0.0.0:5000")
        self.app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    app_instance = VideoApp()
    app_instance.run()


# Пример использования:
# from app import VideoApp
# app = VideoApp()
# app.run()
