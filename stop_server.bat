@echo off
title AWS SAA-C03 Server Stopper
cd /d "%~dp0"

echo ========================================================
echo  [AWS SAA-C03] Stopping server on port 5000...
echo ========================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo  [OK] Server on port 5000 has been stopped successfully.
echo ========================================================
ping 127.0.0.1 -n 3 >nul
