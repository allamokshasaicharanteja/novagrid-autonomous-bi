@echo off
title 🚀 ENTERPRISE LEDGER PAYLOAD GENERATOR
cd /d "%~dp0"
python generate_data.py
echo [SYSTEM]: Ingestion stream dropped to root folder. Closing in 3 seconds...
timeout /t 3 >nul