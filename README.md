# Infra Monitor & Lifecycle Simulator

## Description

**Infra Monitor & Lifecycle Simulator** is a server infrastructure simulation and monitoring system. It allows you to:

1. Simulate multiple servers with CPU, memory, and state metrics.  
2. Log and store requests and events in **PostgreSQL**.  
3. Expose metrics to **Prometheus** for monitoring.  
4. Visualize dashboards and alerts in **Grafana**.  
5. Manage the full server lifecycle: `BOOTING → RUNNING → FAILED → REBOOTING`.  
6. Automatically simulate lifecycle transitions via a background job (`lifecycle_manager.py`).  
7. Improve error handling and observability with centralized logging and exception management.  
8. Run automated tests with `pytest` for server lifecycle and API endpoints (`test_servers.py`).  

Designed for **local** and **cloud environments** (AWS EC2, Docker) with **CI/CD** for automated deployments.

---

## Architecture

```
+------------+      +-------------+
|  Clients   | ---> |  Flask API  |
+------------+      +-------------+
                         |
                         v
                 +---------------+
                 |  servers.py   |
                 |  db.py        |
                 +---------------+
                         |
                         v
                 +--------------------+
                 | PostgreSQL Database|
                 |   infra_monitor    |
                 +--------------------+
                         |
                         v
+-------------+     +----------------+     +---------+
| Prometheus  | <---| Flask Metrics | ---> | Grafana |
+-------------+     +----------------+     +---------+
```


**Components:**

1. **Flask API (`app.py`)** — Endpoints: `/`, `/servers`, `/health`, `/metrics`.  
2. **Database (`db.py`)** — PostgreSQL connection and queries.  
3. **Servers (`servers.py`)** — Simulated servers (CPU, memory, state).  
4. **Lifecycle Manager (`lifecycle_manager.py`)** — Periodic lifecycle state transitions.  
5. **Tests (`test_servers.py`)** — Automated tests for endpoints and lifecycle.  
6. **Prometheus** — Scrapes `/metrics`.  
7. **Grafana** — Dashboards and alerts.  
8. **Docker / Docker Compose** — Local orchestration.  
9. **CI/CD (GitHub Actions)** — Automated testing and deployments.

---

## Technologies

| Component     | Technology / Version        |
|----------------|-----------------------------|
| Backend        | Python 3.13, Flask 2.3.4    |
| Database       | PostgreSQL 15               |
| Monitoring     | Prometheus 2.x, Grafana 10.x |
| Containers     | Docker 28.3.3, Docker Compose 1.29+ |
| CI/CD          | GitHub Actions              |
| Logging        | Python logging (`app.log`)  |
| Testing        | pytest                      |

---

## Installation

### Requirements
- Python **3.13+**  
- Docker & Docker Compose  
- PostgreSQL (local or Dockerized)  
- Prometheus  
- Grafana  
- Homebrew *(optional, for Mac services)*

### Clone repository
```bash
git clone https://github.com/AbelPena02/Infra-Monitor.git
cd Infra-Monitor
```

Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Running Locally
Using Flask and local services
```

Activate environment
```bash
source venv/bin/activate
```
Start Flask API
```bash
python app.py
```
Start Prometheus
```bash
prometheus --config.file=prometheus.yml
```
Start Grafana (Mac)
```bash
brew services start grafana
```
Start PostgreSQL (Mac)
```bash
brew services start postgresql
```
Using Docker Compose
Build containers
```bash
docker-compose build
```
Start stack
```bash
docker-compose up
```
Stop Services
Stop Flask
```bash
Ctrl + C
```
Stop Prometheus
```bash
Ctrl + C
```
Stop Grafana and PostgreSQL (Mac)
```bash
brew services stop grafana
brew services stop postgresql
```
Using Docker
```bash
docker-compose down
```
## Endpoints

| Endpoint                | Method | Description                      | Request Example                         | Response Example                                           |
| ----------------------- | ------ | -------------------------------- | --------------------------------------- | ---------------------------------------------------------- |
| `/`                     | GET    | Home, inserts a request log      | -                                       | -                                                          |
| `/servers`              | GET    | Returns simulated servers        | -                                       | -                                                          |
| `/servers`              | POST   | Creates a new server             | `{"name":"server1","ip":"192.168.0.1"}` | `{ "id": 1, "name":"server1", "ip":"192.168.0.1", ... }`   |
| `/servers/<id>`         | GET    | Returns a specific server        | -                                       | `{ "id": 1, "name":"server1", "ip":"192.168.0.1", ... }`   |
| `/servers/<id>`         | PUT    | Updates a server                 | `{"name":"new_name"}`                   | `{ "id": 1, "name":"new_name", "ip":"192.168.0.1", ... }`  |
| `/servers/<id>`         | DELETE | Deletes a server                 | -                                       | `{ "message": "Server 1 deleted successfully" }`           |
| `/servers/<id>/metrics` | GET    | Returns metrics for a server     | -                                       | `{ "cpu": 50, "memory": 2048, "state": "running", ... }`   |
| `/simulated/<id>`       | DELETE | Deletes a simulated server       | -                                       | `{ "message": "Simulated server 1 deleted successfully" }` |
| `/lifecycle`            | GET    | Returns current lifecycle states |                                         |                                                            |


## Prometheus Metrics
| Metric                        | Description                                   |
| ----------------------------- | --------------------------------------------- |
| `requests_total`              | Total number of requests                      |
| `requests_by_endpoint`        | Requests per endpoint                         |
| `histogram_quantile(0.95, …)` | Latency p95 by endpoint                       |
| `server_cpu_usage`            | CPU usage per server                          |
| `server_memory_usage`         | Memory usage per server                       |
| `server_state`                | Server state (0=FAILED, 1=RUNNING, 2=BOOTING) |


Grafana Dashboards
Recommended panels:

Total requests (Stat / Time series)

Requests by endpoint (Table / Time series)

Latency p95 per endpoint (Time series)

CPU per server (Gauge / Time series)

Server state (Gauge)

Database
Main tables

servers: CPU, memory, state.

requests_log: timestamps of received requests.

Example queries
-- Show tables
\dt

-- Show content
SELECT * FROM servers;
SELECT * FROM requests_log;
CI/CD
GitHub Actions configured to:

Lint and test Python code

Build Docker image

Push to DockerHub (optional)

Automatic deploy to EC2 (optional)

Automated Testing
Framework: pytest

Run tests:
pytest
Coverage includes:

Server creation, update, and deletion

Metrics accuracy

Lifecycle state changes

API health

Test files:

test_servers.py

test_basic.py

