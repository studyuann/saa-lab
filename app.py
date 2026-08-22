import http.server
import socketserver
import webbrowser
import threading
import time
import json
import os
import sys

# Windows 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(DIRECTORY, "user_progress.json")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def do_GET(self):
        # 서버 파일 기반 진행상황 API
        if self.path == "/api/progress":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            
            if os.path.exists(PROGRESS_FILE):
                try:
                    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                        data = f.read()
                except Exception:
                    data = "{}"
            else:
                data = "{}"
            self.wfile.write(data.encode("utf-8"))
            return
        
        super().do_GET()

    def do_POST(self):
        # 서버 파일에 진행상황 실시간 저장 API
        if self.path == "/api/progress":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                progress_data = json.loads(body)
                with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "saved"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def open_browser_delayed(url):
    time.sleep(0.8)
    webbrowser.open(url)

def run_server():
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    url = f"http://localhost:{PORT}"
    
    # 서버 실행 시 브라우저 자동 오픈 (백그라운드 스레드)
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("🚀 AWS SAA-C03 Interactive Quiz Server is running!")
        print(f"👉 브라우저 주소: {url}")
        print(f"📁 풀이 데이터 저장소: user_progress.json (모든 브라우저/기기 공유)")
        print("👉 종료하려면 이 창에서 Ctrl + C 를 누르세요.")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_server()
