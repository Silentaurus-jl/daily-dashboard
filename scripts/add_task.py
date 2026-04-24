#!/usr/bin/env python3
"""
Add a task to the daily dashboard via the GitHub API.

Usage:
  python3 add_task.py <title> <category> [expires] [description]

Arguments:
  title       – Task title (required)
  category    – personal | work | reminder (required)
  expires     – Expiry date as YYYY-MM-DD, or "" for none (optional)
  description – Short description (optional)

Examples:
  python3 add_task.py "Buy groceries" personal 2026-05-01
  python3 add_task.py "Finish report" work 2026-04-30 "Q1 summary for manager"
  python3 add_task.py "Call dentist" reminder "" "Book annual check-up"
"""
import json, sys, subprocess, base64, shutil, tempfile, os
from datetime import date, datetime

REPO = "Silentaurus-jl/daily-dashboard"
FILE = "tasks.json"

def gh(*args, stdin=None):
    exe = shutil.which("gh") or "/c/Program Files/GitHub CLI/gh"
    result = subprocess.run([exe, *args], capture_output=True, text=True, input=stdin)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    title       = sys.argv[1]
    category    = sys.argv[2].lower()
    expires     = sys.argv[3] if len(sys.argv) > 3 else ""
    description = sys.argv[4] if len(sys.argv) > 4 else ""

    if category not in ("personal", "work", "reminder"):
        print(f"Invalid category '{category}'. Use: personal, work, reminder")
        sys.exit(1)

    if expires:
        try:
            datetime.strptime(expires, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date '{expires}'. Use YYYY-MM-DD format.")
            sys.exit(1)

    # Fetch current file + SHA
    file_meta = json.loads(gh("api", f"repos/{REPO}/contents/{FILE}"))
    content   = json.loads(base64.b64decode(file_meta["content"]).decode())
    sha       = file_meta["sha"]

    # Build new task
    task = {
        "id":          str(int(datetime.now().timestamp() * 1000)),
        "title":       title,
        "category":    category,
        "created":     date.today().isoformat(),
        "expires":     expires,
        "description": description,
    }
    content["tasks"].append(task)

    # PUT updated file back via temp file (avoids stdin/--field conflict)
    payload = json.dumps({
        "message": f"add task: {title}",
        "content": base64.b64encode(json.dumps(content, indent=2).encode()).decode(),
        "sha":     sha,
    })
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        gh("api", f"repos/{REPO}/contents/{FILE}", "-X", "PUT", "--input", tmp_path)
    finally:
        os.unlink(tmp_path)

    print(f"✓ Task added: \"{title}\" [{category}]" + (f" — expires {expires}" if expires else ""))

if __name__ == "__main__":
    main()
