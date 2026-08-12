import os
import smtplib
import time
from email.message import EmailMessage


_last_alert_time = {}


def send_email_alert(alert):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    alert_emails = os.getenv("ALERT_EMAILS", "")

    recipients = [
        email.strip()
        for email in alert_emails.split(",")
        if email.strip()
    ]

    if not smtp_username:
        raise RuntimeError("SMTP_USERNAME is not configured")

    if not smtp_password:
        raise RuntimeError("SMTP_PASSWORD is not configured")

    if not recipients:
        raise RuntimeError("ALERT_EMAILS is not configured")

    cooldown = int(os.getenv("ALERT_COOLDOWN", "180"))

    alert_key = (
        alert["event_type"],
        alert.get("source_ip", "unknown"),
    )

    now = time.time()
    last_sent = _last_alert_time.get(alert_key)

    if last_sent is not None and now - last_sent < cooldown:
        remaining = int(cooldown - (now - last_sent))

        print(
            f"[ALERT] Cooldown active for {alert['event_type']} "
            f"({remaining}s remaining)"
        )

        return False

    message = EmailMessage()

    message["Subject"] = (
        f"[SentinelOps] {alert['severity']} - {alert['event_type']}"
    )

    message["From"] = smtp_username
    message["To"] = ", ".join(recipients)

    body = f"""SentinelOps Security Alert

Event Type: {alert['event_type']}
Severity: {alert['severity']}
Source IP: {alert.get('source_ip', 'N/A')}

Message:
{alert['message']}
"""

    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    _last_alert_time[alert_key] = now

    print(
        f"[ALERT] Email sent to {len(recipients)} recipient(s): "
        f"{alert['event_type']} ({alert['severity']})"
    )

    return True
