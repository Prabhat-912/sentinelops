import time
from datetime import datetime, timezone

import psutil

from app.config import config
from app.db import get_connection


def collect_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent

    timestamp = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO metrics (
            timestamp,
            cpu_percent,
            memory_percent,
            disk_percent
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            timestamp,
            cpu_percent,
            memory_percent,
            disk_percent,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "timestamp": timestamp,
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "disk_percent": disk_percent,
    }


def run_collector():
    interval = config["monitoring"]["interval"]

    while True:
        metrics = collect_metrics()
        print(metrics)

        time.sleep(interval)
