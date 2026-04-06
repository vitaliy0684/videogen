#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "[1/4] 🔍 Проверка Python..."
if command -v python3 >/dev/null 2>&1; then
  PY_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PY_CMD=python
else
  echo -e "${RED}❌ ОШИБКА: Python не найден. РЕШЕНИЕ: Установи Python 3.8+.${NC}"
  exit 1
fi

echo -e "[2/4] 🔍 Проверка venv..."
if [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
  echo -e "${GREEN}✅ УСПЕХ: venv активирован.${NC}"
else
  echo -e "${YELLOW}⚠️ ПРЕДУПРЕЖДЕНИЕ: venv не найден.${NC}"
fi

echo -e "[3/4] 🔍 Проверка конфигурации..."
[ -d "generated_videos" ] || mkdir -p "generated_videos"
if [ ! -f "config.py" ]; then
  echo -e "${RED}❌ ОШИБКА: config.py не найден.${NC}"
  exit 1
fi

echo -e "[4/4] 🚀 Запуск Telegram-бота..."
$PY_CMD bot.py || {
  echo -e "${RED}❌ ОШИБКА: Бот не запустился.${NC}"
  echo -e "${YELLOW}🔧 РЕШЕНИЕ: Проверь токен и выполни pip install -r requirements.txt${NC}"
  exit 1
}

# Пример использования:
# bash scripts/run_bot.sh
