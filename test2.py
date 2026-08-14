import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.alerting import send_email_alert
from app.prometheus_metrics import record_email_alert
from app.security import (
    parse_failed_login,
    detect_suspicious_logins,
    save_security_events,
)


# Load local test environment variables.
ENV_FILE = Path(".env")

if ENV_FILE.exists():
    with ENV_FILE.open() as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key] = value


SOURCE_IP = "192.168.1.50"

print("[INFO] Simulating 5 failed login attempts...")
print(f"[INFO] Source IP: {SOURCE_IP}")

base_time = datetime.now(timezone.utc).replace(microsecond=0)

simulated_lines = []

for i in range(5):
    timestamp = base_time - timedelta(seconds=4 * (4 - i))

    line = (
        f"{timestamp.isoformat()} "
        f"Failed password for invalid user test from {SOURCE_IP}"
    )

    simulated_lines.append(line)


# Parse simulated authentication log entries.
events = []

for line in simulated_lines:
    event = parse_failed_login(line)

    if event:
        events.append(event)


print(f"[INFO] Parsed {len(events)} failed login events")

# Run the real SentinelOps detection logic.
alerts = detect_suspicious_logins(events)

if not alerts:
    print("[ERROR] No suspicious login detected.")
    raise SystemExit(1)


for alert in alerts:
    print(
        f"[ALERT] {alert['severity']} - "
        f"{alert['event_type']} - "
        f"{alert['message']}"
    )

    # Save the real security event to SQLite.
    save_security_events([alert])

    # Send the real security alert email.
    try:
        if send_email_alert(alert):
            record_email_alert(alert)
            print("[SUCCESS] Security alert email sent successfully.")
        else:
            print("[INFO] Email was not sent because of cooldown.")
    except Exception as exc:
        print(f"[ERROR] Failed to send security alert email: {exc}")
        raise SystemExit(1)


print("[SUCCESS] Suspicious-login test completed.")
