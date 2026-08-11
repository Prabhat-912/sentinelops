from flask import Flask, jsonify, request

from app.db import get_connection

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "SentinelOps"
    })


@app.route("/metrics", methods=["GET"])
def metrics():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            timestamp,
            cpu_percent,
            memory_percent,
            disk_percent
        FROM metrics
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    connection.close()

    data = [
        {
            "id": row[0],
            "timestamp": row[1],
            "cpu_percent": row[2],
            "memory_percent": row[3],
            "disk_percent": row[4],
        }
        for row in rows
    ]

    return jsonify(data)


@app.route("/events", methods=["GET"])
def events():
    connection = get_connection()

    query = """
        SELECT
            id,
            timestamp,
            event_type,
            severity,
            message
        FROM events
    """

    params = []

    severity = request.args.get("severity")

    if severity:
        query += " WHERE severity = ?"
        params.append(severity.upper())

    query += " ORDER BY id DESC LIMIT 50"

    rows = connection.execute(query, params).fetchall()

    connection.close()

    data = [
        {
            "id": row[0],
            "timestamp": row[1],
            "event_type": row[2],
            "severity": row[3],
            "message": row[4],
        }
        for row in rows
    ]

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
