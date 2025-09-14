Infra Monitor & Lifecycle Simulator

### Description ###

Infra Monitor & Lifecycle Simulator is a server infrastructure simulation and monitoring system. It allows you to:

1.-Simulate multiple servers with CPU, memory, and state metrics.
2.-Log and store requests and events in PostgreSQL.
3.-Expose metrics to Prometheus for monitoring.
4.-Visualize dashboards and alerts in Grafana.
5.-Manage the full server lifecycle: BOOTING → RUNNING → FAILED → REBOOTING.

Designed for local and cloud environments (AWS EC2, Docker) with CI/CD for automated deployments.

### Architecture ###
┌─────────────┐      ┌───────────────┐
│   Clients   │ ---> │   Flask API   │
└─────────────┘      │   (app.py)    │
                     │   Servers.py  │
                     │   DB.py       │
                     └─────┬─────────┘
                           │
                           ▼
                     ┌──────────────┐
                     │ PostgreSQL   │
                     │ infra_monitor│
                     └─────┬────────┘
                           │
                           ▼
┌─────────────┐       ┌───────────────┐       ┌─────────────┐
│ Prometheus  │ <---- │ Flask Metrics │ ----> │ Grafana     │
└─────────────┘       └───────────────┘       └─────────────┘


1.-Flask API (app.py): /, /servers, /health, /metrics.
2.-DB (db.py): PostgreSQL connection.
3.-Servers (servers.py): server simulation (CPU, memory, state).
4.-Prometheus: scrape /metrics.
5.-Grafana: dashboards and alerts.
6.-Docker / Docker Compose: local stack orchestration.
7.-CI/CD: GitHub Actions for tests and deployments.

### Technologies ###
Component	    Technology/Version
Backend	        Python 3.13, Flask 2.3.4
Database	    PostgreSQL 15
Monitoring	    Prometheus 2.x, Grafana 10.x
Containers	    Docker 28.3.3, Docker Compose 1.29+
CI/CD	        GitHub Actions
Logging	        Python logging, app.log


### Installation ###
Requirements

Python 3.13+
Docker & Docker Compose
PostgreSQL (or Dockerized)
Prometheus
Grafana
Homebrew (optional for Mac services)

Clone repository
git clone https://github.com/AbelPena02/Infra-Monitor.git
cd Infra-Monitor

Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### Running Locally ###
Using Flask and local services

# Activate environment
source venv/bin/activate

# Start Flask API
python app.py

# Start Prometheus
prometheus --config.file=prometheus.yml

# Start Grafana (Mac)
brew services start grafana

# Start PostgreSQL (Mac)
brew services start postgresql

Using Docker Compose

# Build containers
docker-compose build

# Start stack
docker-compose up

Stop services
# Stop Flask
# Ctrl + C in terminal

# Stop Prometheus
# Ctrl + C in terminal

# Stop Grafana and PostgreSQL
brew services stop grafana
brew services stop postgresql

# Using Docker
docker-compose down

### Endpoints ###
Endpoint	    Method	    Description
/	            GET	        Home, inserts a request log
/servers	    GET	        Returns simulated servers
/health	        GET	        API and DB status
/metrics	    GET	    Prometheus metrics (CPU, memory, state, requests, latency)


### Prometheus Metrics ###

Total requests: requests_total

Requests by endpoint: requests_by_endpoint

Latency p95 by endpoint: histogram_quantile(0.95, sum(rate(http_request_latency_seconds_bucket[5m])) by (le, endpoint))

CPU per server: server_cpu_usage

Memory per server: server_memory_usage

Server state: server_state (0=FAILED,1=RUNNING,2=BOOTING)

### rafana Dashboards ###

Recommended panels:

Total requests (Stat / Time series)

Requests by endpoint (Table / Time series)

Latency p95 per endpoint (Time series)

CPU per server (Gauge / Time series)

Server state (Gauge)

### Database ###
Main tables

servers: CPU, memory, state.

requests_log: timestamps of received requests.

Example queries
-- Show tables
\dt

-- Show content
SELECT * FROM servers;
SELECT * FROM requests_log;

### CI/CD ###

GitHub Actions configured to:

Lint and test Python code

Build Docker image

Push to DockerHub (optional)

Automatic deploy to EC2 (optional)
