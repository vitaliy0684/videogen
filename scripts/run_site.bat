@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo [1/4] 🔍 Проверка Python...
set "PY_CMD="
for %%P in (py python python3) do (
  where %%P >nul 2>nul
  if not errorlevel 1 (
    set "PY_CMD=%%P"
    goto :python_found
  )
)
:python_found
if "%PY_CMD%"=="" (
  echo ❌ ОШИБКА: Python не установлен. РЕШЕНИЕ: Установи Python 3.8+ и Add to PATH.
  pause
  exit /b 1
)

echo [2/4] 🔍 Проверка venv...
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"

echo [3/4] 🔍 Проверка конфигурации...
if not exist "generated_videos" mkdir "generated_videos"
if not exist "config.py" (
  echo ❌ ОШИБКА: config.py не найден.
  pause
  exit /b 1
)

echo [4/4] 🚀 Запуск Flask-сайта...
start http://127.0.0.1:5000
%PY_CMD% app.py
if errorlevel 1 (
  echo ⚠️ ПРЕДУПРЕЖДЕНИЕ: Порт 5000 уже используется или есть ошибка запуска.
  echo 🔧 РЕШЕНИЕ: Освободи порт 5000 или измени порт в app.py.
)
pause

REM Пример использования:
REM scripts\run_site.bat
