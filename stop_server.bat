@echo off
title AWS SAA-C03 Server Stop
cd /d "%~dp0"
echo [AWS SAA-C03] 5000번 포트 서버를 종료합니다...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo.
echo ========================================================
echo [OK] 서버가 안전하게 종료되었습니다.
echo ========================================================
timeout /t 2 >nul
