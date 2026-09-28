@echo off
title AWS SAA-C03 Interactive Quiz Master
cd /d "%~dp0"
echo AWS SAA-C03 퀴즈 서버를 실행합니다...
start http://localhost:5000
python app.py
pause
