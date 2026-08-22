@echo off
title AWS SAA-C03 Background Server
cd /d "%~dp0"

echo ========================================================
echo  [AWS SAA-C03] Starting Quiz Server in Background...
echo ========================================================

start "" pythonw app.py

echo.
echo  [OK] Server is now running silently in the background!
echo  (You can safely close this IDE and all terminal windows)
echo.
echo  - PC Browser   : http://localhost:5000
echo  - Mobile Wi-Fi : Check console on app.py (e.g. http://172.30.1.3:5000)
echo  - To Stop      : Run stop_server.bat
echo ========================================================
ping 127.0.0.1 -n 4 >nul
