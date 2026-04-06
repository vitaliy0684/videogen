#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

pick_port() {
  local default_port=5000
  if command -v lsof >/dev/null 2>&1 && lsof -i :"$default_port" >/dev/null 2>&1; then
    echo 5001
  else
    echo "$default_port"
  fi
}

echo -e "[1/4] 🔍 Проверка Python..."
if command -v python3 >/dev/null 2>&1; then
  PY_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PY_CMD=python
else
  echo -e "${RED}❌ ОШИБКА: Python не найден.${NC}"
  exit 1
fi

echo -e "[2/4] 🔍 Проверка venv..."
if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
fi

echo -e "[3/4] 🔍 Подготовка папок..."
[ -d "generated_videos" ] || mkdir -p "generated_videos"

PORT="$(pick_port)"
if [ "$PORT" != "5000" ]; then
  echo -e "${YELLOW}⚠️ ПРЕДУПРЕЖДЕНИЕ: Порт 5000 занят, использую $PORT.${NC}"
fi

echo -e "[4/4] 🚀 Запуск Flask-сайта на порту $PORT..."
FLASK_RUN_PORT="$PORT" $PY_CMD app.py || {
  echo -e "${RED}❌ ОШИБКА: Сайт не запустился.${NC}"
  exit 1
}

# Пример использования:
# bash scripts/run_site.sh
