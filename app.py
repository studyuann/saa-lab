import http.server
import socketserver
import socket
import webbrowser
import threading
import time
import json
import os
import sys
import hashlib
import urllib.parse
import asyncio

try:
    import edge_tts
except ImportError:
    edge_tts = None

PORT = int(os.environ.get("PORT", 5000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(DIRECTORY, "user_progress.json")
LOG_FILE = os.path.join(DIRECTORY, "server.log")
AUDIO_CACHE_DIR = os.path.join(DIRECTORY, "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

def get_or_create_tts_audio(text, voice="ko-KR-SunHiNeural", rate="+0%"):
    if not edge_tts:
        return None
    cache_key = f"{voice}_{rate}_{text}".encode("utf-8")
    filename = hashlib.md5(cache_key).hexdigest() + ".mp3"
    filepath = os.path.join(AUDIO_CACHE_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return filepath

    try:
        async def _gen():
            c = edge_tts.Communicate(text, voice, rate=rate)
            await c.save(filepath)
        asyncio.run(_gen())
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
    except Exception as e:
        if sys.stderr:
            sys.stderr.write(f"Edge TTS synthesis error: {e}\n")
    return None

# pythonw (백그라운드/GUI) 실행 시 stdout/stderr가 None이므로 파일로 안전하게 리다이렉트
if sys.stdout is None or sys.stderr is None:
    try:
        log_stream = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stdout = log_stream
        sys.stderr = log_stream
    except Exception:
        pass
else:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def log_message(self, format, *args):
        try:
            if sys.stderr is not None:
                sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")
        except Exception:
            pass

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        
        # SAA 퀴즈 웹앱 서빙 (루트 및 /saa 모두 지원)
        if clean_path in ["/", "/index.html", "/saa", "/saa/", "/saa/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(DIRECTORY, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        # 3. 진행상황 API (/api/progress 및 /saa/api/progress)
        if clean_path in ["/api/progress", "/saa/api/progress"]:
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

        # 4. 퀴즈 데이터 파일 경로 대응
        if clean_path == "/saa/quiz_data.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            with open(os.path.join(DIRECTORY, "quiz_data.json"), "rb") as f:
                self.wfile.write(f.read())
            return

        # 5. 고음질 Edge-TTS 실시간 스트리밍 & 캐시 API (/api/tts 및 /saa/api/tts)
        if clean_path in ["/api/tts", "/saa/api/tts"]:
            query_str = self.path.split("?")[1] if "?" in self.path else ""
            params = urllib.parse.parse_qs(query_str)
            text = params.get("text", [""])[0]
            voice = params.get("voice", ["ko-KR-SunHiNeural"])[0]
            rate = params.get("rate", ["+0%"])[0]

            if not text:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "text parameter is required"}')
                return

            filepath = get_or_create_tts_audio(text, voice, rate)
            if filepath and os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(file_size))
                self.send_header("Cache-Control", "public, max-age=31536000, immutable")
                self.end_headers()
                with open(filepath, "rb") as f:
                    while chunk := f.read(65536):
                        self.wfile.write(chunk)
                return
            else:
                self.send_response(503)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Edge-TTS unavailable"}')
                return

        super().do_GET()

    def do_POST(self):
        clean_path = self.path.split("?")[0]
        # 서버 파일에 진행상황 실시간 저장 API
        if clean_path in ["/api/progress", "/saa/api/progress"]:
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

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def open_browser_delayed(url):
    time.sleep(0.8)
    webbrowser.open(url)

def run_server():
    os.chdir(DIRECTORY)
    local_url = f"http://localhost:{PORT}"
    wifi_ip = get_local_ip()
    wifi_url = f"http://{wifi_ip}:{PORT}"
    
    # 로컬 PC 실행 시에만 브라우저 자동 오픈 (클라우드 환경 제외)
    if "RENDER" not in os.environ and "PORT" not in os.environ:
        threading.Thread(target=open_browser_delayed, args=(local_url,), daemon=True).start()
    
    # 멀티스레드 비동기 HTTP 서버 (다중 탭/모바일 동시 접속 병목 방지)
    server_class = getattr(http.server, "ThreadingHTTPServer", http.server.HTTPServer)
    server_class.allow_reuse_address = True
    
    with server_class(("", PORT), Handler) as httpd:
        print("=" * 65)
        print("🚀 AWS SAA-C03 Interactive Master Web Server")
        print("=" * 65)
        print(f"💻 [이 PC에서 접속]       : {local_url}")
        print(f"📱 [스마트폰/태블릿 Wi-Fi] : {wifi_url}")
        print(f"📁 [진행상황 저장소]       : user_progress.json (실시간 영구 동기화)")
        print("-" * 65)
        print("💡 동일한 Wi-Fi에 연결된 스마트폰이나 태블릿에서 위 📱 주소로 접속하세요!")
        print("👉 서버를 종료하려면 이 창에서 Ctrl + C 를 누르세요.")
        print("=" * 65)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_server()
