@echo off
title Document Intelligence System - Public Demo

set "PROJECT_ROOT=C:\Users\Admin\OneDrive\Documents\New folder (2)\document-intelligence-system"
set "CLOUDFLARED_DIR=C:\cloudflared"

echo ============================================================
echo Document Intelligence System - Public Demo
echo ============================================================
echo.

echo [1/2] Starting FastAPI...
start "FastAPI - Document Intelligence System" cmd /k "cd /d "%PROJECT_ROOT%" && call "%PROJECT_ROOT%\venv\Scripts\activate.bat" && uvicorn app.main:app --reload"

timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Cloudflare Quick Tunnel...
start "Cloudflare Tunnel - Document Intelligence System" cmd /k "cd /d "%CLOUDFLARED_DIR%" && cloudflared.exe tunnel --protocol http2 --url http://localhost:8000"

echo.
echo ============================================================
echo Public demo startup commands launched.
echo ============================================================
echo.
echo Keep both opened terminal windows running.
echo Cloudflare will display your temporary public URL.
echo.
pause