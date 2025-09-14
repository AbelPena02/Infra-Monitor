from flask import Flask, Response, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from db import db, Server
from servers import get_all_servers, servers_bp, get_simulated_metrics_for_db_servers
import logging
import time
from sqlalchemy import text
from logger import logger

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://monitor:monitor123@localhost:5432/infra_monitor"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

@app.route("/servers", methods=["POST"])
def create_server():
    data = request.get_json()
    
    if not data.get("name") or not data.get("cpu_usage") or not data.get("memory_usage") or not data.get("state"):
        logger.warning("Invalid server creation attempt: %s", data)
        return {"error": "Missing required fields"}, 400

    cpu = data["cpu_usage"]
    memory = data["memory_usage"]
    if not (0 <= cpu <= 100) or not (0 <= memory <= 100):
        logger.warning("CPU or memory out of range: %s", data)
        return {"error": "CPU or memory out of range"}, 400

    if data["state"] not in ["BOOTING", "RUNNING", "FAILED"]:
        logger.warning("Invalid state value: %s", data)
        return {"error": "Invalid state value"}, 400

    server = Server(
        name=data["name"],
        cpu_usage=cpu,
        memory_usage=memory,
        state=data["state"]
    )
    db.session.add(server)
    db.session.commit()

    logger.info("Server created: %s", data["name"])
    return {"status": "success", "id": server.id}, 201

@app.route("/servers/<int:server_id>", methods=["PUT"])
def update_server(server_id):
    data = request.get_json()
    server = Server.query.get(server_id)
    if not server:
        logger.warning("Update failed, server_id=%d not found", server_id)
        return {"error": "Server not found"}, 404

    cpu = data.get("cpu_usage", server.cpu_usage)
    memory = data.get("memory_usage", server.memory_usage)
    state = data.get("state", server.state)

    if not (0 <= cpu <= 100) or not (0 <= memory <= 100):
        logger.warning("CPU or memory out of range: %s", data)
        return {"error": "CPU or memory out of range"}, 400
    if state not in ["BOOTING", "RUNNING", "FAILED"]:
        logger.warning("Invalid state value: %s", data)
        return {"error": "Invalid state value"}, 400

    server.cpu_usage = cpu
    server.memory_usage = memory
    server.state = state
    db.session.commit()

    logger.info("Server updated: server_id=%d", server_id)
    return {"status": "success"}, 200

@app.route("/servers/<int:server_id>", methods=["DELETE"])
def delete_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        logger.warning("Delete failed, server_id=%d not found", server_id)
        return {"error": "Server not found"}, 404

    db.session.delete(server)
    db.session.commit()
    logger.info("Server deleted: server_id=%d", server_id)
    return {"status": "deleted"}, 200

@app.route("/servers/<int:server_id>", methods=["GET"])
def get_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        logger.warning("Get failed, server_id=%d not found", server_id)
        return {"error": "Server not found"}, 404

    logger.info("Server retrieved: server_id=%d", server_id)
    return {
        "server": {
            "id": server.id,
            "name": server.name,
            "cpu_usage": server.cpu_usage,
            "memory_usage": server.memory_usage,
            "state": server.state
        }
    }, 200

@app.route("/simulated-servers/<server_id>", methods=["DELETE"])
def delete_simulated_server(server_id):
    servers = get_all_servers()
    index = next((i for i, s in enumerate(servers) if s["id"] == server_id), None)
    if index is not None:
        servers.pop(index)
        logger.info("Deleted simulated server %s", server_id)
        return {"status": "deleted"}, 200
    return {"error": "server not found"}, 404


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(host="0.0.0.0", port=5000, debug=True)
