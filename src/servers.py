import random
import time
from flask import Blueprint, request, jsonify
from db import db, Server 

class SimulatedServer:
    def __init__(self, server_id):
        self.id = str(server_id)
        self.state = "RUNNING"
        self.cpu_usage = 0.0
        self.memory_usage = 0
        self.uptime = 0
        self.last_checked = time.time()

    def update(self):
        now = time.time()
        elapsed = now - self.last_checked
        self.last_checked = now

        if random.random() < 0.05:
            self.state = "FAILED"
            self.cpu_usage = 0.0
            self.memory_usage = 0
            self.uptime = 0
        else:
            if self.state == "FAILED" and random.random() < 0.3:
                self.state = "BOOTING"
                self.uptime = 0
            if self.state == "BOOTING":
                if random.random() < 0.5:
                    self.state = "RUNNING"
            if self.state == "RUNNING":
                self.cpu_usage = round(random.uniform(10, 90), 2)
                self.memory_usage = random.randint(256, 2048)
                self.uptime += int(elapsed)

        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "uptime": self.uptime
        }

simulated_servers = [SimulatedServer(f"srv-{i}") for i in range(1, 4)]
_sim_map = {}

def get_all_servers():
    return [srv.update() for srv in simulated_servers]

def _ensure_sim_for_dbserver(db_server):
    key = str(db_server.id)
    if key not in _sim_map:
        _sim_map[key] = SimulatedServer(key)
    return _sim_map[key]

def get_simulated_metrics_for_db_servers():
    rows = Server.query.all()
    result = []
    for r in rows:
        sim = _ensure_sim_for_dbserver(r)
        m = sim.update()
        m['id'] = r.id
        m['hostname'] = getattr(r, "hostname", None)
        m['status'] = getattr(r, "status", None)
        result.append(m)
    return result

def _remove_sim_for_dbserver_id(server_id):
    _sim_map.pop(str(server_id), None)

servers_bp = Blueprint("servers", __name__)

@servers_bp.route("/", methods=["POST"])
def create_server():
    data = request.json
    server = Server(
        hostname=data["hostname"],
        ip_address=data["ip_address"],
        status=data.get("status", "RUNNING")
    )
    db.session.add(server)
    db.session.commit()
    _ensure_sim_for_dbserver(server)
    return jsonify({
        "id": server.id,
        "hostname": server.hostname,
        "ip_address": server.ip_address,
        "status": server.status
    }), 201

@servers_bp.route("/", methods=["GET"])
def get_servers():
    servers = Server.query.all()
    return jsonify([
        {"id": s.id, "hostname": s.hostname, "ip_address": s.ip_address, "status": s.status}
        for s in servers
    ])

@servers_bp.route("/<int:server_id>", methods=["GET"])
def get_server(server_id):
    server = Server.query.get_or_404(server_id)
    return jsonify({
        "id": server.id,
        "hostname": server.hostname,
        "ip_address": server.ip_address,
        "status": server.status
    })

@servers_bp.route("/<int:server_id>", methods=["PUT"])
def update_server(server_id):
    server = Server.query.get_or_404(server_id)
    data = request.json
    server.hostname = data.get("hostname", server.hostname)
    server.ip_address = data.get("ip_address", server.ip_address)
    server.status = data.get("status", server.status)
    db.session.commit()
    return jsonify({"message": "Server updated"})

@servers_bp.route("/<int:server_id>", methods=["DELETE"])
def delete_server(server_id):
    server = Server.query.get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    _remove_sim_for_dbserver_id(server_id)
    return jsonify({"message": "Server deleted"})

@servers_bp.route("/<int:server_id>/metrics", methods=["GET"])
def server_metrics(server_id):
    server = Server.query.get_or_404(server_id)
    sim = _ensure_sim_for_dbserver(server)
    m = sim.update()
    return jsonify({
        "server_id": server.id,
        "hostname": server.hostname,
        "metrics": {
            "cpu": m["cpu_usage"],
            "memory": m["memory_usage"],
            "uptime": m["uptime"],
            "state": m["state"]
        }
    })

@servers_bp.route("/simulated/<server_id>", methods=["DELETE"])
def delete_simulated(server_id):
    global simulated_servers
    index = next((i for i, s in enumerate(simulated_servers) if s.id == server_id), None)
    if index is not None:
        simulated_servers.pop(index)
        return jsonify({"message": f"Simulated server {server_id} deleted"}), 200
    return jsonify({"error": "Server not found"}), 404
