import os
from pathlib import Path

from app.alerting import send_email_alert


ENV_FILE = Path(".env")

if ENV_FILE.exists():
    with ENV_FILE.open() as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key]=value


test_alert = {
    "event_type": "TEST_ALERT",
    "severity": "CRITICAL",
    "source_ip": "10.10.10.99",
    "message": "This is a test security alert from SentinelOps.",
}

try:
    if send_email_alert(test_alert):
        print("[SUCCESS] Test email sent successfully.")
    else:
        print("[INFO] Email was not sent.")
except Exception as exc:
    print(f"[ERROR] Failed to send test email: {exc}")
