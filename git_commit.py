import subprocess
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def run_cmd(cmd):
    print(f">> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr)
    return res.returncode

# 1. Check if git repo exists
if not os.path.exists(".git"):
    run_cmd("git init")

# 2. Configure user name/email if not set
run_cmd("git config user.name")
run_cmd("git config user.email")

# 3. Add files
run_cmd("git add .")

# 4. Status
run_cmd("git status")

# 5. Commit
commit_msg = "feat: Complete AWS SAA-C03 725-Question Interactive Master Platform"
run_cmd(f'git commit -m "{commit_msg}"')

# 6. Log
run_cmd("git log -n 3 --oneline")
