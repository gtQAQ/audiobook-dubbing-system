@echo off
title Audiobook Dubbing System
echo Starting Audiobook Dubbing System...
echo Project URL: http://127.0.0.1:8000

:: Open the browser
start http://127.0.0.1:8000

:: Navigate to backend and start server
cd backend
..\venv\Scripts\uvicorn main:app --reload

pause