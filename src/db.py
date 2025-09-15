from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), default="RUNNING")
    cpu_usage = db.Column(db.Float, default=0.0)
    memory_usage = db.Column(db.Integer, default=0)
    uptime = db.Column(db.Integer, default=0)
