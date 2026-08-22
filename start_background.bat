@echo off
title AWS SAA-C03 Background Server
cd /d "%~dp0"
echo [AWS SAA-C03] 백그라운드 서버를 시작합니다...
start "" pythonw app.py
echo.
echo ========================================================
echo [OK] 서버가 백그라운드에서 실행되었습니다.
echo IDE 창을 닫아도 서버가 계속 유지됩니다.
echo.
echo - PC 접속   : http://localhost:5000
echo - 서버 종료 : stop_server.bat 실행
echo ========================================================
timeout /t 3 >nul
