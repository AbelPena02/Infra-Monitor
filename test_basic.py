import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from app import app, db

@pytest.fixture
def client():
    app.config.from_object("config.TestConfig")
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert "db" in data

def test_simulated_servers(client):
    r = client.get("/simulated-servers")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]

def test_metrics_endpoint(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    txt = r.get_data(as_text=True)
    assert ("requests_total" in txt) or ("server_cpu_usage" in txt)
