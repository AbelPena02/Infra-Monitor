from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(20), default="RUNNING")
