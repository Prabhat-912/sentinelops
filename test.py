from app.alerting import send_email_alert

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
