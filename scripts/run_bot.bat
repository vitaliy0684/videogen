@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo [1/4] 🔍 Проверка Python...
set "PY_CMD="
for %%P in (venv\Scripts\python.exe python py python3) do (
  if "%%P"=="venv\Scripts\python.exe" (
    if exist "%%P" (
      %%P -c "import telebot" >nul 2>nul
      if not errorlevel 1 (
        set "PY_CMD=%%P"
        goto :python_found
      )
    )
  ) else (
    where %%P >nul 2>nul
    if not errorlevel 1 (
      %%P -c "import telebot" >nul 2>nul
      if not errorlevel 1 (
        set "PY_CMD=%%P"
        goto :python_found
      )
    )
  )
)
:python_found
if "%PY_CMD%"=="" (
  echo ❌ ОШИБКА: Не найден Python с установленным telebot.
  echo 🔧 РЕШЕНИЕ: Выполни команду python -m pip install -r requirements.txt
  echo 📋 ИНФОРМАЦИЯ: Если у тебя несколько Python, запускай бот тем же интерпретатором, где ставились пакеты.
  pause
  exit /b 1
)
echo ✅ УСПЕХ: Выбран интерпретатор %PY_CMD%
for /f "delims=" %%I in ('%PY_CMD% -c "import sys; print(sys.executable)"') do set "PY_PATH=%%I"
echo 📋 ИНФОРМАЦИЯ: Путь Python: !PY_PATH!

echo [2/4] 🔍 Проверка venv...
if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
  echo ✅ УСПЕХ: venv активирован ^(если выбран venv-python, он уже используется^).
) else (
  echo ⚠️ ПРЕДУПРЕЖДЕНИЕ: venv не найден, использую системный Python.
)

echo [3/4] 🔍 Проверка config.py и папки generated_videos...
if not exist "generated_videos" mkdir "generated_videos"
if not exist "config.py" (
  echo ❌ ОШИБКА: config.py не найден. РЕШЕНИЕ: Создай файл и добавь API_KEY/BOT_TOKEN.
  pause
  exit /b 1
)

echo [4/4] 🚀 Запуск Telegram-бота...
%PY_CMD% bot.py
if errorlevel 1 (
  echo ❌ ОШИБКА: Бот не запустился. ПРОВЕРЬ: 1) Токен правильный? 2) Интернет? 3) Зависимости установлены?
  echo 🔧 РЕШЕНИЕ: %PY_CMD% -m pip install -r requirements.txt
)
pause

REM Пример использования:
REM scripts\run_bot.bat
