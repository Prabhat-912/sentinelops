# SentinelOps

SentinelOps is a lightweight security and system monitoring agent built with Python.

## Features

- System metrics collection (CPU, Memory, Disk)
- Security event detection
- Suspicious login monitoring
- Email alerting
- REST API
- Prometheus metrics endpoint
- SQLite storage
- Systemd service support

## Project Structure

app/
- alerting.py
- api.py
- collector.py
- config.py
- db.py
- prometheus_metrics.py
- rules.py
- runner.py
- security.py

config/
- config.yaml

systemd/
- sentinelops.service
- sentinelops-api.service

## Installation

Clone the repository:

    git clone https://github.com/Prabhat-912/sentinelops.git
    cd sentinelops

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## Email Configuration

Copy the example environment file:

    cp .env.example .env

Edit the `.env` file and configure:

    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your-email@gmail.com
    SMTP_PASSWORD=your-app-password
    ALERT_EMAILS=user1@example.com,user2@example.com,user3@example.com
    ALERT_COOLDOWN=180

Load the variables:

    source .env

## Run SentinelOps

Start the monitoring agent:

    python -m app.runner

Start the API:

    python -m app.api

## API Endpoints

Health check:

    http://127.0.0.1:5001/health

Metrics:

    http://127.0.0.1:5001/metrics

Events:

    http://127.0.0.1:5001/events

Prometheus metrics:

    http://127.0.0.1:5001/prometheus

## Test Email Alerting

Run:

    python test.py

A successful test should show:

    [ALERT] Email sent to 3 recipient(s): TEST_ALERT (CRITICAL)
    [SUCCESS] Test email sent successfully.

## Systemd

Install the services:

    sudo cp systemd/*.service /etc/systemd/system/
    sudo systemctl daemon-reload

Enable them:

    sudo systemctl enable sentinelops
    sudo systemctl enable sentinelops-api

Start them:

    sudo systemctl start sentinelops
    sudo systemctl start sentinelops-api

Check status:

    sudo systemctl status sentinelops
    sudo systemctl status sentinelops-api

## Prometheus

SentinelOps exposes Prometheus metrics at:

    http://127.0.0.1:5001/prometheus

Prometheus can scrape this endpoint to monitor:

- CPU usage
- Memory usage
- Disk usage
- Security alerts
- Email alerts

## Database

SentinelOps uses SQLite for local storage.

The database is created automatically when SentinelOps starts.

Runtime database files are ignored by Git.

