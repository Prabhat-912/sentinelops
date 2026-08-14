# SentinelOps

SentinelOps is a lightweight Python-based security and system monitoring agent designed to detect suspicious activity, collect system metrics, store events locally, expose monitoring metrics through Prometheus, and send security alerts through Gmail SMTP.

## Features

* CPU, memory, and disk monitoring
* Failed-login and suspicious-login detection
* Security event storage using SQLite
* Email alerting through Gmail SMTP
* REST API built with Flask
* Prometheus metrics endpoint
* Grafana monitoring dashboard
* Systemd service support
* Automatic service startup after reboot

## Architecture

```text
                    ┌──────────────────────┐
                    │      SentinelOps     │
                    │   Python Monitoring  │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
          ┌──────────────┐            ┌──────────────┐
          │    SQLite    │            │   Flask API  │
          │ Metrics/Events│           │    :5001     │
          └──────────────┘            └──────┬───────┘
                                             │
                                      /prometheus
                                             │
                                             ▼
                                     ┌──────────────┐
                                     │  Prometheus  │
                                     │    :9090     │
                                     └──────┬───────┘
                                            │
                                            ▼
                                     ┌──────────────┐
                                     │    Grafana   │
                                     │    :3000     │
                                     └──────────────┘

Security Event
      │
      ▼
SentinelOps Detection
      │
      ▼
Email Alert
```

## Project Structure

```text
sentinelops/
├── app/
│   ├── __init__.py
│   ├── alerting.py
│   ├── api.py
│   ├── collector.py
│   ├── config.py
│   ├── db.py
│   ├── prometheus_metrics.py
│   ├── rules.py
│   ├── runner.py
│   └── security.py
│
├── config/
│   └── config.yaml
│
├── systemd/
│   ├── sentinelops.service
│   └── sentinelops-api.service
│
├── tests/
├── test.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Prabhat-912/sentinelops.git
cd sentinelops
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Email Configuration

SentinelOps uses Gmail SMTP with a Gmail App Password.

### Manual test configuration

Create a local `.env` file:

```bash
vim .env
```

Configure:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@gmail.com
SMTP_PASSWORD=your-gmail-app-password
ALERT_EMAILS=recipient1@gmail.com,recipient2@gmail.com,recipient3@gmail.com
ALERT_COOLDOWN=180
```

Protect the file:

```bash
chmod 600 .env
```

`.env` must never be committed to GitHub.

### Persistent systemd configuration

For automatic alerts after reboot, store the SMTP configuration in:

```bash
sudo mkdir -p /etc/sentinelops
sudo vim /etc/sentinelops/smtp.env
```

Use:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@gmail.com
SMTP_PASSWORD=your-gmail-app-password
ALERT_EMAILS=recipient1@gmail.com,recipient2@gmail.com,recipient3@gmail.com
ALERT_COOLDOWN=180
```

Protect the file:

```bash
sudo chmod 600 /etc/sentinelops/smtp.env
```

The SentinelOps systemd service loads this file automatically.

After changing the sender, App Password, recipients, or cooldown:

```bash
sudo systemctl daemon-reload
sudo systemctl restart sentinelops
```

Check the service:

```bash
sudo systemctl status sentinelops --no-pager
```

### Change the sender account

Edit:

```bash
sudo vim /etc/sentinelops/smtp.env
```

Change:

```env
SMTP_USERNAME=new-sender@gmail.com
SMTP_PASSWORD=new-gmail-app-password
```

Then restart:

```bash
sudo systemctl restart sentinelops
```

### Change alert recipients

Edit:

```bash
sudo vim /etc/sentinelops/smtp.env
```

Change:

```env
ALERT_EMAILS=user1@gmail.com,user2@gmail.com,user3@gmail.com
```

Then:

```bash
sudo systemctl restart sentinelops
```

### Change alert cooldown

The cooldown prevents the same alert from generating repeated emails too quickly.

```env
ALERT_COOLDOWN=180
```

The value is in seconds.

## Running SentinelOps

### Run manually

```bash
source .venv/bin/activate
python -m app.runner
```

### Start the REST API manually

```bash
python -m app.api
```

The Flask development server runs on port `5000`.

The systemd/Gunicorn deployment runs the API on port `5001`.

## Systemd

Install the services:

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Enable automatic startup:

```bash
sudo systemctl enable sentinelops
sudo systemctl enable sentinelops-api
```

Start the services:

```bash
sudo systemctl start sentinelops
sudo systemctl start sentinelops-api
```

Check status:

```bash
sudo systemctl status sentinelops --no-pager
sudo systemctl status sentinelops-api --no-pager
```

After a reboot, the services start automatically.

## API Endpoints

Health check:

```text
http://127.0.0.1:5001/health
```

Latest stored metrics:

```text
http://127.0.0.1:5001/metrics
```

Security events:

```text
http://127.0.0.1:5001/events
```

Prometheus metrics:

```text
http://127.0.0.1:5001/prometheus
```

Example health check:

```bash
curl http://localhost:5001/health
```

## Prometheus

Prometheus runs on:

```text
http://localhost:9090
```

Configure Prometheus to scrape:

```yaml
- job_name: 'sentinelops'
  scrape_interval: 10s
  metrics_path: '/prometheus'
  static_configs:
    - targets: ['127.0.0.1:5001']
```

Validate the configuration:

```bash
promtool check config /etc/prometheus/prometheus.yml
```

Restart Prometheus:

```bash
sudo systemctl restart prometheus
```

Verify the SentinelOps target:

```bash
curl -s http://localhost:9090/api/v1/targets
```

The SentinelOps target should report:

```text
health: up
```

### Available Prometheus metrics

```text
sentinelops_cpu_usage_percent
sentinelops_memory_usage_percent
sentinelops_disk_usage_percent
sentinelops_security_alerts_total
sentinelops_email_alerts_total
```

Example query:

```promql
sentinelops_cpu_usage_percent
```

## Grafana

Grafana runs on:

```text
http://localhost:3000
```

Add Prometheus as a Grafana data source:

```text
URL: http://localhost:9090
```

Recommended dashboard panels:

* SentinelOps CPU usage
* SentinelOps memory usage
* SentinelOps disk usage
* Security alert count
* Email alert count

Example PromQL queries:

```promql
sentinelops_cpu_usage_percent
```

```promql
sentinelops_memory_usage_percent
```

```promql
sentinelops_disk_usage_percent
```

```promql
sentinelops_security_alerts_total
```

```promql
sentinelops_email_alerts_total
```

## Test Email Alerting

The test script generates a synthetic `TEST_ALERT`.

Run:

```bash
source .venv/bin/activate
python test.py
```

Expected output:

```text
[ALERT] Email sent to 3 recipient(s): TEST_ALERT (CRITICAL)
[SUCCESS] Test email sent successfully.
```

This test does **not** represent a real failed-login event.

Actual security emails are generated automatically when SentinelOps detects suspicious activity.

Example real alert:

```text
Event Type: SUSPICIOUS_LOGIN
Severity: CRITICAL
Source IP: 192.168.1.50

Message:
5 failed login attempts from 192.168.1.50 within 60 seconds
```

## Security Monitoring

SentinelOps monitors authentication logs for failed login attempts.

When repeated failed login attempts from the same source exceed the configured threshold, SentinelOps generates a security event such as:

```text
SUSPICIOUS_LOGIN
```

with an appropriate severity level.

The event is stored in SQLite and can trigger an email alert.

## Database

SentinelOps uses SQLite for local storage.

The database is created automatically when SentinelOps starts.

Runtime database files are ignored by Git.

## Verification

Check all core services:

```bash
sudo systemctl status sentinelops --no-pager
sudo systemctl status sentinelops-api --no-pager
sudo systemctl status prometheus --no-pager
sudo systemctl status grafana-server --no-pager
```

Verify the API:

```bash
curl http://localhost:5001/health
```

Verify Prometheus:

```bash
curl http://localhost:9090/-/ready
```

Verify Grafana:

```bash
curl -I http://localhost:3000
```

## Security Notes

Never commit:

```text
.env
/etc/sentinelops/smtp.env
```

Never place a real Gmail App Password in:

* GitHub
* README files
* source code
* screenshots
* commit messages

Use Gmail App Passwords rather than the normal Gmail account password for SMTP authentication.

## License

This project is intended as a portfolio and learning project.

