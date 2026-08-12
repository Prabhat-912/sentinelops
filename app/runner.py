import time

from app.db import initialize_database
from app.collector import collect_metrics
from app.rules import check_metrics, save_events
from app.security import (
    read_auth_log,
    parse_failed_login,
    detect_suspicious_logins,
    save_security_events,
)
from app.config import config
from app.alerting import send_email_alert


def run_security_checks():
    lines = read_auth_log()

    events = []

    for line in lines:
        event = parse_failed_login(line)

        if event:
            events.append(event)

    print(f"[INFO] Collected {len(events)} failed login events")

    alerts = detect_suspicious_logins(events)

    if alerts:
        save_security_events(alerts)

        for alert in alerts:
            print(
                f"[ALERT] {alert['severity']} - "
                f"{alert['event_type']} - "
                f"{alert['message']}"
            )

            try:
                send_email_alert(alert)
            except Exception as exc:
                print(f"[ERROR] Failed to send email alert: {exc}")
    else:
        print("[OK] No suspicious login activity detected")


def run_monitoring_checks():
    metrics = collect_metrics()

    print(
        f"[METRICS] CPU={metrics['cpu_percent']}% "
        f"MEMORY={metrics['memory_percent']}% "
        f"DISK={metrics['disk_percent']}%"
    )

    events = check_metrics(metrics)

    if events:
        save_events(events)

        for event in events:
            print(
                f"[ALERT] {event['severity']} - "
                f"{event['event_type']} - "
                f"{event['message']}"
            )

            try:
                send_email_alert(event)
            except Exception as exc:
                print(f"[ERROR] Failed to send email alert: {exc}")


def main():
    initialize_database()

    interval = config["monitoring"]["interval"]

    print("[INFO] SentinelOps started")
    print(f"[INFO] Monitoring interval: {interval} seconds")

    while True:
        try:
            run_monitoring_checks()
            run_security_checks()

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[INFO] SentinelOps stopped")
            break


if __name__ == "__main__":
    main()
