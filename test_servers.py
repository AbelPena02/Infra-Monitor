import pytest
from app import app, db
from db import Server

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_server(client):
    response = client.post("/servers/", json={
        "hostname": "test-server",
        "ip_address": "192.168.1.100"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["hostname"] == "test-server"
    assert data["status"] == "RUNNING"

def test_get_servers_empty(client):
    response = client.get("/servers/")
    assert response.status_code == 200
    assert response.get_json() == []

def test_update_server(client):
    response = client.post("/servers/", json={
        "hostname": "server1",
        "ip_address": "10.0.0.1"
    })
    server_id = response.get_json()["id"]
    
    response = client.put(f"/servers/{server_id}", json={
        "hostname": "updated-server",
        "status": "FAILED"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Server updated"

    response = client.get(f"/servers/{server_id}")
    data = response.get_json()
    assert data["hostname"] == "updated-server"
    assert data["status"] == "FAILED"

def test_delete_server(client):
    response = client.post("/servers/", json={
        "hostname": "todelete",
        "ip_address": "10.10.10.10"
    })
    server_id = response.get_json()["id"]

    response = client.delete(f"/servers/{server_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Server deleted"

    response = client.get(f"/servers/{server_id}")
    assert response.status_code == 404
