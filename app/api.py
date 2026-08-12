from flask import Flask, jsonify, request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.db import get_connection
from app.prometheus_metrics import update_metrics_from_database

app = Flask(__name__)

@app.route("/prometheus", methods=["GET"])
def prometheus():
    update_metrics_from_database()

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )



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
