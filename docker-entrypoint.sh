#!/bin/sh

echo "Initializing SentinelOps database..."
python -c "from app.db import initialize_database; initialize_database()"

echo "Starting SentinelOps API..."
exec gunicorn --workers 2 --bind 0.0.0.0:5000 app.api:app
