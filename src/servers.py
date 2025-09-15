from flask import Flask, Response, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from db import db, Server
from servers import get_all_servers, servers_bp, get_simulated_metrics_for_db_servers, simulated_servers
import logging
import time
from sqlalchemy import text
from logger import logger
from config import Config
import threading

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config) 

db.init_app(app)
app.register_blueprint(servers_bp, url_prefix="/servers")

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# -----------------------------
# PROMETHEUS METRICS
# -----------------------------
requests_total = Counter(
    'requests_total',
    'Total number of requests'
)

requests_by_endpoint = Counter(
    'requests_by_endpoint',
    'HTTP requests by endpoint and method',
    ['endpoint', 'method']
)

request_latency = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds',
    ['endpoint']
)

server_cpu = Gauge(
    'server_cpu_usage',
    'CPU usage percentage',
    ['server_id']
)

server_memory = Gauge(
    'server_memory_usage',
    'Memory usage MB',
    ['server_id']
)

server_state = Gauge(
    'server_state',
    'Server state (0=FAILED,1=RUNNING,2=BOOTING)',
    ['server_id']
)

# -----------------------------
# REQUEST TIMING
# -----------------------------
@app.before_request
def before_req():
    request._start_time = time.time()

@app.after_request
def after_req(response):
    try:
        endpoint = request.path
        method = request.method
        elapsed = time.time() - getattr(request, "_start_time", time.time())
        requests_total.inc()
        requests_by_endpoint.labels(endpoint=endpoint, method=method).inc()
        if endpoint != "/metrics":
            request_latency.labels(endpoint=endpoint).observe(elapsed)
    except Exception as e:
        logging.error(f"Metrics instrumentation error: {e}")
    return response

# -----------------------------
# BACKGROUND SCHEDULER
# -----------------------------
def background_server_updates(interval=5):
    while True:
        with app.app_context():
            for srv in simulated_servers:
                srv.update()
        time.sleep(interval)

# Start the background thread
thread = threading.Thread(target=background_server_updates, daemon=True)
thread.start()

# -----------------------------
# ENDPOINTS
# -----------------------------
@app.route("/")
def home():
    logging.info("New request received at /")
    status = "Infra Monitor API running!"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        logging.error(f"DB connection error: {e}")
        status += " (DB error)"
    return status

@app.route("/simulated-servers")
def simulated_servers_endpoint():
    logging.info("Simulated servers endpoint called")
    servers = get_all_servers()
    return jsonify(servers)

@app.route("/health")
def health():
    status = {"status": "ok", "db": "connected"}
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        status["db"] = "error"
        logging.error(f"Health DB check failed: {e}")
    return jsonify(status)

@app.route("/metrics")
def metrics():
    try:
        db_count = Server.query.count()
    except Exception:
        db_count = 0

    if db_count > 0:
        servers_metrics = get_simulated_metrics_for_db_servers()
    else:
        servers_metrics = get_all_servers()

    state_map = {"FAILED": 0, "RUNNING": 1, "BOOTING": 2}

    for srv in servers_metrics:
        sid = str(srv.get("id", "unknown"))
        cpu = float(srv.get("cpu_usage", 0))
        mem = float(srv.get("memory_usage", 0))
        state = srv.get("state", "FAILED")

        server_cpu.labels(server_id=sid).set(cpu)
        server_memory.labels(server_id=sid).set(mem)
        server_state.labels(server_id=sid).set(state_map.get(state, 0))

    logger.info("Metrics scraped for %d servers", len(servers_metrics))
    return Response(generate_latest(), mimetype="text/plain")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
