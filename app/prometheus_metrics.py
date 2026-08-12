from prometheus_client import Gauge, Counter

from app.db import get_connection


cpu_usage = Gauge(
    "sentinelops_cpu_usage_percent",
    "Current CPU usage percentage",
)

memory_usage = Gauge(
    "sentinelops_memory_usage_percent",
    "Current memory usage percentage",
)

disk_usage = Gauge(
    "sentinelops_disk_usage_percent",
    "Current disk usage percentage",
)

security_alerts = Counter(
    "sentinelops_security_alerts_total",
    "Total number of SentinelOps security alerts",
)

email_alerts = Counter(
    "sentinelops_email_alerts_total",
    "Total number of email alerts sent by SentinelOps",
)


def update_metrics_from_database():
    connection = get_connection()

    row = connection.execute(
        """
        SELECT cpu_percent, memory_percent, disk_percent
        FROM metrics
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if row:
        cpu_usage.set(row[0])
        memory_usage.set(row[1])
        disk_usage.set(row[2])

    alert_count = connection.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    connection.close()

    security_alerts._value.set(alert_count)


def update_system_metrics(metrics):
    cpu_usage.set(metrics["cpu_percent"])
    memory_usage.set(metrics["memory_percent"])
    disk_usage.set(metrics["disk_percent"])


def record_security_alert():
    security_alerts.inc()


def record_email_alert():
    email_alerts.inc()
