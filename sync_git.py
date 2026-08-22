import json
import os
import sys
import re
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

transcript_path = r"C:\Users\ANN\.gemini\antigravity-ide\brain\a9860161-2dd5-45fd-bbfa-03c3e6178c02\.system_generated\logs\transcript.jsonl"

messages = []

def clean_user_content(text):
    match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', text, re.DOTALL)
    if match:
        clean = match.group(1).strip()
    else:
        clean = text.strip()
    clean = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', clean, flags=re.DOTALL)
    clean = re.sub(r'<[^>]+>', '', clean)
    return clean.strip()

if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                step_type = obj.get("type", "")
                content = obj.get("content", "")

                if step_type == "USER_INPUT" and content:
                    if "CHECKPOINT" in content and "User Requests" in content:
                        continue
                    if "<SYSTEM_MESSAGE>" in content and "<USER_REQUEST>" not in content:
                        continue
                    
                    cleaned = clean_user_content(content)
                    if cleaned:
                        messages.append({
                            "role": "User",
                            "content": cleaned
                        })
                elif step_type == "PLANNER_RESPONSE" and content:
                    if content.strip():
                        messages.append({
                            "role": "Assistant",
                            "content": content.strip()
                        })
            except Exception as e:
                pass

# Update Markdown
md_lines = []
md_lines.append("# 📜 AWS SAA-C03 플랫폼 개발 및 전체 대화 기록 (최종본)")
md_lines.append(f"- **날짜**: 2026-08-22")
md_lines.append(f"- **참여자**: 사용자(studyuann) & Antigravity AI Assistant")
md_lines.append(f"- **프로젝트**: AWS SAA-C03 725문항 인터랙티브 퀴즈 & 실전 모의고사 플랫폼 (`saa-lab`)")
md_lines.append(f"- **총 대화 턴 수**: {len(messages)} 건")
md_lines.append("\n---\n")

for i, msg in enumerate(messages, 1):
    if msg["role"] == "User":
        md_lines.append(f"### 👤 사용자 (User)\n")
        md_lines.append(f"{msg['content']}\n")
    else:
        md_lines.append(f"### 🤖 Antigravity Assistant\n")
        md_lines.append(f"{msg['content']}\n")
    md_lines.append("\n---\n")

with open("conversation_export.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

# Update HTML Viewer
html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>AWS SAA-C03 세션 전체 대화 기록 (Export)</title>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0b0f19;
      color: #f8fafc;
      line-height: 1.75;
      padding: 2.5rem 1.25rem;
      max-width: 920px;
      margin: 0 auto;
    }}
    h1 {{
      font-size: 1.65rem;
      border-bottom: 2px solid #334155;
      padding-bottom: 0.8rem;
      margin-bottom: 1rem;
      color: #38bdf8;
    }}
    .meta-card {{
      background: #1e293b;
      padding: 1.1rem 1.4rem;
      border-radius: 10px;
      margin-bottom: 2rem;
      font-size: 0.92rem;
      color: #94a3b8;
      border: 1px solid #334155;
    }}
    .msg {{
      margin-bottom: 1.5rem;
      padding: 1.25rem 1.4rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }}
    .msg-user {{
      background: #1e293b;
      border-left: 4px solid #ff9900;
    }}
    .msg-assistant {{
      background: #131b2e;
      border-left: 4px solid #38bdf8;
    }}
    .role {{
      font-weight: 700;
      font-size: 0.9rem;
      margin-bottom: 0.6rem;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .role-user {{ color: #fbbf24; }}
    .role-assistant {{ color: #38bdf8; }}
    .content {{
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.95rem;
    }}
    pre, code {{
      font-family: 'JetBrains Mono', monospace;
      background: #070a12;
      border-radius: 4px;
      padding: 2px 6px;
    }}
    pre {{
      padding: 1rem;
      overflow-x: auto;
      border: 1px solid #334155;
    }}
  </style>
</head>
<body>
  <h1>📜 AWS SAA-C03 플랫폼 개발 세션 전체 대화 기록</h1>
  <div class="meta-card">
    <p>• <strong>프로젝트</strong>: AWS SAA-C03 Interactive Master (saa-lab)</p>
    <p>• <strong>총 대화 턴 수</strong>: {len(messages)} 건</p>
    <p>• <strong>최종 업데이트 일시</strong>: 2026-08-22</p>
  </div>
"""

for msg in messages:
    is_u = msg["role"] == "User"
    cls_box = "msg-user" if is_u else "msg-assistant"
    cls_role = "role-user" if is_u else "role-assistant"
    icon = "👤" if is_u else "🤖"
    escaped_content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_template += f"""
  <div class="msg {cls_box}">
    <div class="role {cls_role}">{icon} {msg['role']}</div>
    <div class="content">{escaped_content}</div>
  </div>
"""

html_template += """
</body>
</html>
"""

with open("conversation_export.html", "w", encoding="utf-8") as f:
    f.write(html_template)

# Git add, commit, push
subprocess.run(['git', 'add', '-A'])
commit_res = subprocess.run(['git', 'commit', '-m', 'chore: Synchronize full project state, background server scripts, and conversation export'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit output:\n", commit_res.stdout)

push_res = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Push output:\n", push_res.stdout, push_res.stderr)
