"""
Модуль запроса генерации видео через Proxy API.
"""

import argparse
import base64
import logging
import time
import traceback

import requests
from openai import OpenAI

import config


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def _validate_config() -> None:
    if not config.API_KEY or "ваш" in config.API_KEY.lower():
        raise ValueError(
            "❌ ОШИБКА: API_KEY отсутствует. РЕШЕНИЕ: Зарегистрируйся на proxyapi.ru, "
            "получи ключ и добавь его в config.py или .env"
        )


def _normalize_seconds(seconds_value) -> str:
    """
    API принимает seconds только строкой: '4', '8' или '12'.
    """
    value = str(seconds_value).strip()
    allowed = {"4", "8", "12"}
    if value not in allowed:
        raise ValueError(
            "❌ ОШИБКА: Некорректное значение VIDEO_SECONDS. "
            "РЕШЕНИЕ: Укажи 4, 8 или 12 в config.py/.env"
        )
    return value


def _extract_video_url(video_response) -> str:
    # Поддерживаем несколько вариантов структуры ответа API.
    for field in ("url", "video_url", "output_url"):
        if hasattr(video_response, field):
            value = getattr(video_response, field)
            if value:
                return value
    if hasattr(video_response, "data") and video_response.data:
        first = video_response.data[0]
        for field in ("url", "video_url", "output_url"):
            value = getattr(first, field, None)
            if value:
                return value
    raise RuntimeError(
        "❌ ОШИБКА: Не найден URL сгенерированного видео в ответе API. "
        "РЕШЕНИЕ: Проверь баланс, модель и формат ответа Proxy API."
    )


def _to_dict(obj):
    if obj is None:
        return {}
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict()
        except Exception:
            pass
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {"value": str(obj)}


def _find_first_http_url(node):
    if isinstance(node, str) and node.startswith(("http://", "https://")):
        return node
    if isinstance(node, dict):
        priority_keys = ("url", "video_url", "output_url", "content_url", "download_url")
        for key in priority_keys:
            value = node.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
        for value in node.values():
            found = _find_first_http_url(value)
            if found:
                return found
    if isinstance(node, list):
        for item in node:
            found = _find_first_http_url(item)
            if found:
                return found
    return None


def _find_first_b64_video(node):
    if isinstance(node, dict):
        for key in ("b64_json", "base64", "video_base64"):
            value = node.get(key)
            if isinstance(value, str) and len(value) > 100:
                try:
                    return base64.b64decode(value)
                except Exception:
                    pass
        for value in node.values():
            found = _find_first_b64_video(value)
            if found:
                return found
    if isinstance(node, list):
        for item in node:
            found = _find_first_b64_video(item)
            if found:
                return found
    return None


def _find_first_text_by_keys(node, keys):
    keys_lower = {k.lower() for k in keys}
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower() in keys_lower and isinstance(value, str) and value.strip():
                return value.strip()
        for value in node.values():
            found = _find_first_text_by_keys(value, keys)
            if found:
                return found
    if isinstance(node, list):
        for item in node:
            found = _find_first_text_by_keys(item, keys)
            if found:
                return found
    return None


def _extract_failure_reason(job_obj) -> str:
    payload = _to_dict(job_obj)
    # Часто встречающиеся поля с причиной ошибки в API-ответах.
    reason = _find_first_text_by_keys(
        payload,
        {
            "error",
            "message",
            "reason",
            "failure_reason",
            "last_error",
            "error_message",
            "detail",
        },
    )
    return reason or "Причина не указана API."


def _get_job_id(job_obj) -> str:
    payload = _to_dict(job_obj)
    return str(payload.get("id") or getattr(job_obj, "id", "")).strip()


def _get_status(job_obj) -> str:
    payload = _to_dict(job_obj)
    status = payload.get("status") or getattr(job_obj, "status", "unknown")
    return str(status).strip() or "unknown"


def _create_job(client: OpenAI, prompt: str, video_seconds: str):
    # В некоторых версиях SDK нет ресурса client.videos, поэтому используем REST fallback.
    if hasattr(client, "videos"):
        logger.info("📋 Использую OpenAI SDK videos API.")
        return client.videos.create(
            model=config.VIDEO_MODEL,
            prompt=prompt,
            seconds=video_seconds,
        )

    logger.warning("⚠️ SDK не поддерживает client.videos, переключаюсь на HTTP fallback.")
    create_url = f"{config.PROXY_API_URL}/videos"
    headers = {"Authorization": f"Bearer {config.API_KEY}"}
    payload = {
        "model": config.VIDEO_MODEL,
        "prompt": prompt,
        "seconds": video_seconds,
    }
    response = requests.post(create_url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _retrieve_job(client: OpenAI, job_id: str):
    if hasattr(client, "videos"):
        return client.videos.retrieve(job_id)

    retrieve_url = f"{config.PROXY_API_URL}/videos/{job_id}"
    headers = {"Authorization": f"Bearer {config.API_KEY}"}
    response = requests.get(retrieve_url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def generate_video(prompt: str) -> str:
    """
    Генерирует видео по текстовому промпту и сохраняет в папку generated_videos.
    Возвращает путь до сохраненного файла.
    """
    _validate_config()
    if not prompt.strip():
        raise ValueError("❌ ОШИБКА: Пустой промпт. РЕШЕНИЕ: Введи описание видео.")

    config.GENERATED_VIDEOS_PATH.mkdir(parents=True, exist_ok=True)
    video_seconds = _normalize_seconds(config.VIDEO_SECONDS)
    client = OpenAI(api_key=config.API_KEY, base_url=config.PROXY_API_URL)

    try:
        logger.info("[1/4] 🎬 Начинаю генерацию видео...")
        job = _create_job(client, prompt, video_seconds)

        job_id = _get_job_id(job)
        if not job_id:
            raise RuntimeError(
                "❌ ОШИБКА: API не вернул id задачи. РЕШЕНИЕ: Проверь ключ и доступность API."
            )

        logger.info("[2/4] ⏳ Задача создана: %s", job_id)
        status = "queued"
        poll = 0
        max_polls = 120

        while status in {"queued", "in_progress"} and poll < max_polls:
            poll += 1
            logger.info("[3/4] 🔄 Проверка статуса (%s/%s)...", poll, max_polls)
            current = _retrieve_job(client, job_id)
            status = _get_status(current)
            logger.info("📋 Текущий статус: %s", status)
            if status in {"queued", "in_progress"}:
                time.sleep(5)
            else:
                job = current

        if status != "completed":
            failure_reason = _extract_failure_reason(job)
            raise RuntimeError(
                f"❌ ОШИБКА: Генерация завершилась со статусом '{status}'. "
                f"ПРИЧИНА: {failure_reason}. "
                "РЕШЕНИЕ: Проверь баланс API, доступность модели и текст промпта."
            )

        logger.info("[4/4] 📥 Скачиваю готовое видео...")
        payload = _to_dict(job)
        video_bytes = _find_first_b64_video(payload)
        if video_bytes:
            content = video_bytes
            logger.info("📋 Получены байты видео напрямую (base64).")
        else:
            video_url = _find_first_http_url(payload)
            if not video_url:
                # Fallback на распространенный endpoint контента задачи.
                job_id = _get_job_id(job)
                if job_id:
                    fallback_url = f"{config.PROXY_API_URL}/videos/{job_id}/content"
                    headers = {"Authorization": f"Bearer {config.API_KEY}"}
                    fallback_response = requests.get(fallback_url, headers=headers, timeout=120)
                    if fallback_response.ok and fallback_response.content:
                        content = fallback_response.content
                        logger.info("📋 Видео получено через fallback endpoint content.")
                    else:
                        payload_keys = ", ".join(sorted(payload.keys())) if isinstance(payload, dict) else "unknown"
                        raise RuntimeError(
                            "❌ ОШИБКА: Не найден URL/контент видео в ответе API. "
                            f"Контекст: keys=[{payload_keys}], status={status}. "
                            "РЕШЕНИЕ: Проверь баланс API, модель и формат ответа Proxy API."
                        )
                else:
                    raise RuntimeError(
                        "❌ ОШИБКА: API не вернул ссылку/контент и id задачи. "
                        "РЕШЕНИЕ: Проверь ключ API и повтори запрос."
                    )
            else:
                response = requests.get(video_url, timeout=120)
                response.raise_for_status()
                content = response.content

        out_file = config.GENERATED_VIDEOS_PATH / f"video_{int(time.time())}.mp4"
        out_file.write_bytes(content)
        logger.info("✅ УСПЕХ: Видео сохранено: %s", out_file)
        return str(out_file)

    except Exception as exc:
        logger.error("❌ ОШИБКА: %s", exc)
        logger.debug("Traceback:\n%s", traceback.format_exc())
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Тест генерации видео через Proxy API")
    parser.add_argument("--prompt", default="Кот в космосе, кинематографичный стиль")
    args = parser.parse_args()
    result = generate_video(args.prompt)
    print(f"✅ УСПЕХ: Видео создано: {result}")


# Пример использования:
# from request import generate_video
# path = generate_video("Кот в космосе")
# print(path)
