from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re
from app.db import get_connection
from app.config import config


FAILED_LOGIN_PATTERNS = [
    re.compile(r"Failed password for .* from (?P<ip>\S+)"),
    re.compile(r"authentication failure.*rhost=(?P<ip>\S+)"),
]


def parse_failed_login(line):
    for pattern in FAILED_LOGIN_PATTERNS:
        match = pattern.search(line)

        if match:
            return {
                "timestamp": line[:25],
                "source_ip": match.group("ip"),
                "event_type": "FAILED_LOGIN",
            }

    return None


def detect_suspicious_logins(events):
    threshold = config["security"]["failed_login_threshold"]
    window = config["security"]["failed_login_window"]

    attempts = defaultdict(list)
    suspicious = []

    for event in events:
        ip = event["source_ip"]

        try:
            timestamp = datetime.fromisoformat(
                event["timestamp"]
            )
        except ValueError:
            continue

        attempts[ip].append(timestamp)

        cutoff = timestamp - timedelta(seconds=window)

        attempts[ip] = [
            attempt
            for attempt in attempts[ip]
            if attempt >= cutoff
        ]

        if len(attempts[ip]) >= threshold:
            suspicious.append({
                "event_type": "SUSPICIOUS_LOGIN",
                "severity": "CRITICAL",
                "source_ip": ip,
                "message": (
                    f"{len(attempts[ip])} failed login attempts "
                    f"from {ip} within {window} seconds"
                ),
            })

            attempts[ip] = []  # prevent repeated alerts

    return suspicious


def read_auth_log():
    log_path = Path(config["security"]["auth_log"])

    if not log_path.exists():
        return []

    with log_path.open("r", encoding="utf-8", errors="replace") as file:
        return file.readlines()




def save_security_events(events):
    if not events:
        return

    connection = get_connection()

    for event in events:
        timestamp = datetime.now(timezone.utc).isoformat()

        connection.execute(
            """
            INSERT INTO events (
                timestamp,
                event_type,
                severity,
                message
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                event["event_type"],
                event["severity"],
                event["message"],
            ),
        )

    connection.commit()
    connection.close()
