@echo off
chcp 65001 >nul
title Lanzador Prototipo - Client Management API

echo ================================================
echo   Levantando PROTOTIPO (backend + panel)
echo ================================================
echo.

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo [ERROR] No encuentro el entorno virtual en:
  echo    %PY%
  echo Crealo o ajusta la ruta antes de seguir.
  pause
  exit /b 1
)

echo [1/2] Levantando BACKEND (API) en http://127.0.0.1:8000 ...
start "Backend API 8000" cmd /k "cd /d "%ROOT%backend" && "%PY%" -m uvicorn src.main:app --reload --port 8000"

echo [2/2] Levantando PANEL (frontend) en http://localhost:5173 ...
start "Panel Frontend 5173" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo Listo. Se abrieron DOS ventanas nuevas.
echo   - Backend API ......... http://127.0.0.1:8000/docs
echo   - Panel web ........... http://localhost:5173
echo.
echo Espera unos segundos y abri el panel en el navegador.
echo Para APAGAR: cerra las dos ventanas nuevas (o Ctrl+C en cada una).
echo.
pause
