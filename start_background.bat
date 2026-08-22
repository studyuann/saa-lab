@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo  🚀 AWS SAA-C03 백그라운드 서버를 시작합니다...
echo ========================================================

start "" pythonw app.py

echo.
echo ✅ 서버가 백그라운드에서 완전히 독립 실행되었습니다!
echo 💡 IDE 창을 닫아도 서버가 계속 유지됩니다.
echo.
echo 💻 PC 접속: http://localhost:5000
echo 📱 모바일 Wi-Fi 접속 가능
echo.
echo 🛑 서버를 종료하고 싶을 때는 [stop_server.bat] 을 실행하세요.
echo ========================================================
timeout /t 4 >nul
