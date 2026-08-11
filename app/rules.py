from datetime import datetime, timezone

from app.config import config
from app.db import get_connection


def check_metrics(metrics):
    events = []

    thresholds = config["monitoring"]

    if metrics["cpu_percent"] >= thresholds["cpu_threshold"]:
        events.append({
            "event_type": "HIGH_CPU",
            "severity": "WARNING",
            "message": f"CPU usage is {metrics['cpu_percent']}%"
        })

    if metrics["memory_percent"] >= thresholds["memory_threshold"]:
        events.append({
            "event_type": "HIGH_MEMORY",
            "severity": "WARNING",
            "message": f"Memory usage is {metrics['memory_percent']}%"
        })

    if metrics["disk_percent"] >= thresholds["disk_threshold"]:
        events.append({
            "event_type": "HIGH_DISK",
            "severity": "WARNING",
            "message": f"Disk usage is {metrics['disk_percent']}%"
        })

    return events


def save_events(events):
    if not events:
        return

    timestamp = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    for event in events:
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
