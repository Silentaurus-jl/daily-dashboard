#!/usr/bin/env python3
"""
Set or change the dashboard password.
The hash is stored in tasks.json and shared across all devices.

Usage:
  python3 set_password.py
"""
import json, base64, hashlib, shutil, subprocess, tempfile, os, getpass

REPO = "Silentaurus-jl/daily-dashboard"
FILE = "tasks.json"

def gh(*args, stdin=None):
    exe = shutil.which("gh") or "/c/Program Files/GitHub CLI/gh"
    result = subprocess.run([exe, *args], capture_output=True, text=True, input=stdin)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        raise SystemExit(1)
    return result.stdout

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    password = getpass.getpass("New password: ")
    if len(password) < 4:
        print("Password must be at least 4 characters.")
        raise SystemExit(1)
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        raise SystemExit(1)

    # Fetch current file
    file_meta = json.loads(gh("api", f"repos/{REPO}/contents/{FILE}"))
    content   = json.loads(base64.b64decode(file_meta["content"]).decode())
    sha       = file_meta["sha"]

    content["password_hash"] = sha256(password)

    payload = json.dumps({
        "message": "chore: update dashboard password",
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

    print("✓ Password updated. All devices will use the new password immediately.")

if __name__ == "__main__":
    main()
