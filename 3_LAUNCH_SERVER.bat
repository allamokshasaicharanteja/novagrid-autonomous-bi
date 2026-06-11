@echo off
title 🌐 LIVE PIPELINE PUBLIC INTERNET EDGE NODE
echo =======================================================
echo 🌟 INITIALIZING PUBLIC BI DASHBOARD BROADCAST LINK
echo =======================================================
echo [SYSTEM]: Deploying built-in HTTP listener node on Port 8000...
echo [STATUS]: Local web stream online at http://localhost:8000
echo.
echo [INSTRUCTION]: Open a separate cmd prompt and run: ngrok http 8000
echo.
cd /d "%~dp0"
python -m http.server 8000 --bind 0.0.0.0
pause